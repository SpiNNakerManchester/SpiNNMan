# Copyright (c) 2015 The University of Manchester
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
from threading import RLock
import time
from types import TracebackType
from typing import (Callable, Dict, Generic, List, Optional, Set, TypeVar,
                    cast)
from typing_extensions import TypeAlias
from spinnman.messages.scp.enums import SCPResult
from spinnman.exceptions import SpinnmanTimeoutException, SpinnmanIOException
from spinnman.constants import SCP_TIMEOUT, N_RETRIES
from spinnman.connections.udp_packet_connections import SCAMPConnection
from spinnman.messages.scp.abstract_messages import AbstractSCPRequest
from spinnman.messages.scp.abstract_messages import AbstractSCPResponse

#: Type of responses.
#: :meta private:
R = TypeVar("R", bound=AbstractSCPResponse)
#: Type of response-accepting callbacks.
#: :meta private:
CB: TypeAlias = Callable[[R], None]  # pylint: disable=invalid-name
#: Type of error-handling callbacks.
#: :meta private:
ECB: TypeAlias = Callable[  # pylint: disable=invalid-name
    [AbstractSCPRequest[R], Exception, TracebackType, SCAMPConnection], None]

MAX_SEQUENCE = 65536
RETRY_CODES = frozenset([
    SCPResult.RC_TIMEOUT, SCPResult.RC_P2P_TIMEOUT, SCPResult.RC_LEN,
    SCPResult.RC_P2P_NOREPLY, SCPResult.RC_P2P_BUSY])

# Keep a global track of the sequence numbers used
_next_sequence = 0
_next_sequence_lock = RLock()


class SCPRequestPipeLine(Generic[R]):
    """
    Allows a set of SCP requests to be grouped together in a communication
    across a number of channels for a given connection.

    This class implements an SCP windowing, first suggested by Andrew Mundy.
    This extends the idea by having both send and receive windows.
    These are represented by the n_channels and the
    intermediate_channel_waits parameters respectively.  This seems to
    help with the timeout issue; when a timeout is received, all requests
    for which a reply has not been received can also timeout.
    """
    __slots__ = (
        "_callbacks",
        "_connection",
        "_error_callbacks",
        "_in_progress",
        "_intermediate_channel_waits",
        "_n_channels",
        "_n_resent",
        "_n_retries",
        "_n_retry_code_resent",
        "_n_timeouts",
        "_non_fail_retry_codes",
        "_packet_timeout",
        "_retry_reason",
        "_request_data",
        "_requests",
        "_retries",
        "_send_time")

    def __init__(self, connection: SCAMPConnection, n_channels: int = 1,
                 intermediate_channel_waits: int = 0,
                 n_retries: int = N_RETRIES,
                 packet_timeout: float = SCP_TIMEOUT,
                 non_fail_retry_codes: Optional[Set[SCPResult]] = None):
        """
        :param connection:
            The connection over which the communication is to take place
        :param n_channels: The number of requests to send before checking
            for responses.  If `None`, this will be determined automatically
        :param intermediate_channel_waits: The number of outstanding
            responses to wait for before continuing sending requests.
            If `None`, this will be determined automatically
        :param n_retries: The number of times to resend any packet for any
            reason before an error is triggered
        :param packet_timeout: The number of elapsed seconds after
            sending a packet before it is considered a timeout.
        :param non_fail_retry_codes: Codes that could retry but won't fail, or
            None if there are no such codes
        """
        self._connection = connection
        self._n_channels = n_channels
        self._intermediate_channel_waits = intermediate_channel_waits
        self._n_retries = n_retries
        self._packet_timeout = packet_timeout

        if (self._n_channels is not None and
                self._intermediate_channel_waits is None):
            self._intermediate_channel_waits = self._n_channels - 8
            if self._intermediate_channel_waits < 0:
                self._intermediate_channel_waits = 0

        # A dictionary of sequence number -> requests in progress
        self._requests: Dict[int, AbstractSCPRequest] = dict()
        self._request_data: Dict[int, bytes] = dict()

        # A dictionary of sequence number -> number of retries for the packet
        self._retries: Dict[int, int] = dict()

        # A dictionary of sequence number -> callback function for response
        self._callbacks: Dict[int, Optional[CB]] = dict()

        # A dictionary of sequence number -> callback function for errors
        self._error_callbacks: Dict[int, ECB] = dict()

        # A dictionary of sequence number -> retry reason
        self._retry_reason: Dict[int, List[str]] = dict()

        # The number of responses outstanding
        self._in_progress = 0

        # The number of timeouts that occurred
        self._n_timeouts = 0

        # The number of packets that have been resent
        self._n_resent = 0
        self._n_retry_code_resent = 0
        self._non_fail_retry_codes: Set[SCPResult]
        if non_fail_retry_codes is None:
            self._non_fail_retry_codes = set()
        else:
            self._non_fail_retry_codes = non_fail_retry_codes
        # self._token_bucket = TokenBucket(43750, 4375000)
        # self._token_bucket = TokenBucket(3408, 700000)

    @staticmethod
    def __get_next_sequence_number() -> int:
        """
        Get the next number from the global sequence, applying appropriate
        wrapping rules as the sequence numbers have a fixed number of bits.

        :return: The next number in the sequence.
        """
        # pylint: disable=global-statement
        global _next_sequence
        with _next_sequence_lock:
            sequence = _next_sequence
            _next_sequence = (sequence + 1) % MAX_SEQUENCE
        return sequence

    def send_request(
            self, request: AbstractSCPRequest[R], callback: Optional[CB],
            error_callback: ECB) -> None:
        """
        Add an SCP request to the set to be sent.

        :param request: The SCP request to be sent
        :param callback:
            A callback function to call when the response has been received;
            takes a :py:class:`SCPResponse` as a parameter, or `None` if the
            response doesn't need to be processed
        :param error_callback:
            A callback function to call when an error is found when processing
            the message; takes the original :py:class:`AbstractSCPRequest`, the
            exception caught and a list of tuples of (filename, line number,
            function name, text) as a traceback
        """
        # If the connection has not been measured
        if self._n_channels is None:
            if self._connection.is_ready_to_receive():
                self._n_channels = self._in_progress + 8
                if self._n_channels < 12:
                    self._n_channels = 12
                self._intermediate_channel_waits = self._n_channels - 8

        # If all the channels are used, start to receive packets
        while (self._n_channels is not None and
                self._in_progress >= self._n_channels):
            self._do_retrieve(
                self._intermediate_channel_waits, self._packet_timeout)

        # Get the next sequence to be used
        sequence = self.__get_next_sequence_number()

        # Update the packet and store required details
        request.scp_request_header.sequence = sequence
        request_data = self._connection.get_scp_data(request)
        self._requests[sequence] = request
        self._request_data[sequence] = request_data
        self._retries[sequence] = self._n_retries
        self._callbacks[sequence] = callback
        self._error_callbacks[sequence] = error_callback
        self._retry_reason[sequence] = list()

        # Send the request, keeping track of how many are sent
        # self._token_bucket.consume(284)
        self._connection.send(request_data)
        self._in_progress += 1

    def finish(self) -> None:
        """
        Indicate the end of the packets to be sent.  This must be called
        to ensure that all responses are received and handled.
        """
        while self._in_progress > 0:
            self._do_retrieve(0, self._packet_timeout)

    @property
    def n_timeouts(self) -> int:
        """
        The number of timeouts that occurred."""
        return self._n_timeouts

    @property
    def n_channels(self) -> int:
        """
        The number of requests to send before checking for responses."""
        return self._n_channels

    @property
    def n_resent(self) -> int:
        """
        The number of packets that have been resent."""
        return self._n_resent

    @property
    def n_retry_code_resent(self) -> int:
        """
        The number of resends due to reasons for which automated retry is
        the correct response in-protocol."""
        return self._n_retry_code_resent

    def _remove_record(self, seq: int) -> None:
        if seq in self._requests:
            del self._requests[seq]
        del self._request_data[seq]
        del self._retries[seq]
        del self._callbacks[seq]
        del self._error_callbacks[seq]
        del self._retry_reason[seq]

    def _single_retrieve(self, timeout: float) -> None:
        # Receive the next response
        result, seq, raw_data, offset = \
            self._connection.receive_scp_response(timeout)

        # Only process responses which have matching requests
        if seq in self._requests:
            self._in_progress -= 1
            request_sent = self._requests[seq]

            # If the response can be retried, retry it
            if result in RETRY_CODES:
                try:
                    time.sleep(0.1)
                    self._resend(seq, request_sent, str(result))
                    self._n_retry_code_resent += 1
                    return
                except Exception as e:  # pylint: disable=broad-except
                    if result not in self._non_fail_retry_codes:
                        self._error_callbacks[seq](
                            request_sent, e,
                            cast(TracebackType, sys.exc_info()[2]),
                            self._connection)
                        self._remove_record(seq)
                        return

            # No retry is possible and not failed - try constructing the result
            try:
                response = request_sent.get_scp_response()
                response.read_bytestring(raw_data, offset)
                cb = self._callbacks[seq]
                if cb is not None:
                    cb(response)
            except Exception as e:  # pylint: disable=broad-except
                self._error_callbacks[seq](
                    request_sent, e,
                    cast(TracebackType, sys.exc_info()[2]),
                    self._connection)

            # Remove the sequence from the outstanding responses
            self._remove_record(seq)

    def _handle_receive_timeout(self) -> None:
        self._n_timeouts += 1

        # If there is a timeout, all packets remaining are resent
        to_remove = list()
        for seq, request_sent in self._requests.items():
            self._in_progress -= 1
            try:
                self._resend(seq, request_sent, "timeout")
            except Exception as e:  # pylint: disable=broad-except
                self._error_callbacks[seq](
                    request_sent, e, cast(TracebackType, sys.exc_info()[2]),
                    self._connection)
                to_remove.append(seq)

        for seq in to_remove:
            self._remove_record(seq)

    def _resend(self, seq: int, request_sent: AbstractSCPRequest,
                reason: str) -> None:
        if self._retries[seq] <= 0:
            # Report timeouts as timeout exception

            self._retry_reason[seq].append(reason)
            if all(reason == "timeout" for reason in self._retry_reason[seq]):
                raise SpinnmanTimeoutException(
                    request_sent,
                    self._packet_timeout)

            # Report any other exception
            raise SpinnmanIOException(
                f"Errors sending request {request_sent} to "
                f"{request_sent.sdp_header.destination_chip_x}, "
                f"{request_sent.sdp_header.destination_chip_y}, "
                f"{request_sent.sdp_header.destination_cpu} over "
                f"{self._n_retries} retries: {self._retry_reason[seq]}")

        # If the request can be retried, retry it
        self._retries[seq] -= 1
        self._in_progress += 1
        self._requests[seq] = request_sent
        self._retry_reason[seq].append(reason)
        self._connection.send(self._request_data[seq])
        self._n_resent += 1

    def _do_retrieve(self, n_packets: int, timeout: float) -> None:
        """
        Receives responses until there are only n_packets responses left.

        :param n_packets:
            The number of packets that can remain after running
        """
        # While there are still more packets in progress than some threshold
        while self._in_progress > n_packets:
            try:
                # Receive the next response
                self._single_retrieve(timeout)
            except SpinnmanTimeoutException:
                self._handle_receive_timeout()
