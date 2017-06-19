import sys
import time

from spinnman.messages.scp.enums import SCPResult
from spinnman.exceptions import SpinnmanTimeoutException

MAX_SEQUENCE = 65536

# Keep a global track of the sequence numbers used
_next_sequence = 0


class SCPRequestPipeLine(object):
    """ Allows a set of SCP requests to be grouped together in a communication\
        across a number of channels for a given connection.

        This class implements an SCP windowing, first suggested by Andrew\
        Mundy.  This extends the idea by having both send and receive windows.\
        These are represented by the n_channels and the\
        intermediate_channel_waits parameters respectively.  This seems to\
        help with the timeout issue; when a timeout is received, all requests\
        for which a reply has not been received can also timeout.
    """

    def __init__(self, connection, n_channels=1,
                 intermediate_channel_waits=0,
                 retry_codes=set([SCPResult.RC_TIMEOUT,
                                  SCPResult.RC_P2P_TIMEOUT,
                                  SCPResult.RC_LEN,
                                  SCPResult.RC_P2P_NOREPLY]),
                 n_retries=3, packet_timeout=0.5):
        """
        :param connection: The connection over which the communication is to\
                    take place
        :param n_channels: The number of requests to send before checking for\
                    responses.  If None, this will be determined automatically
        :param intermediate_channel_waits: The number of outstanding responses\
                    to wait for before continuing sending requests.  If None,\
                    this will be determined automatically
        :param retry_codes: The set of response codes that will be retried
        :param n_retries: The number of times to resend any packet for any\
                    reason before an error is triggered
        :param packet_timeout: The number of elapsed seconds after sending a\
                    packet before it is considered a timeout.
        """
        self._connection = connection
        self._n_channels = n_channels
        self._intermediate_channel_waits = intermediate_channel_waits
        self._retry_codes = retry_codes
        self._n_retries = n_retries
        self._packet_timeout = packet_timeout

        if (self._n_channels is not None and
                self._intermediate_channel_waits is None):
            self._intermediate_channel_waits = self._n_channels - 8
            if self._intermediate_channel_waits < 0:
                self._intermediate_channel_waits = 0

        # A dictionary of sequence number -> requests in progress
        self._requests = dict()
        self._request_data = dict()

        # A dictionary of sequence number -> time at which sequence was sent
        self._times_sent = dict()

        # A dictionary of sequence number -> number of retries for the packet
        self._retries = dict()

        # A dictionary of sequence number -> callback function for response
        self._callbacks = dict()

        # A dictionary of sequence number -> callback function for errors
        self._error_callbacks = dict()

        self._send_time = dict()

        # The number of responses outstanding
        self._in_progress = 0

        # The number of timeouts that occured
        self._n_timeouts = 0

        # The number of packets that have been resent
        self._n_resent = 0
        self._n_retry_code_resent = 0

        # self._token_bucket = TokenBucket(43750, 4375000)
        # self._token_bucket = TokenBucket(3408, 700000)

    def send_request(self, request, callback, error_callback):
        """ Add an SCP request to the set to be sent

        :param request: The SCP request to be sent
        :param callback: A callback function to call when the response has\
                    been received; takes SCPResponse as a parameter, or None\
                    if the response doesn't need to be processed
        :param error_callback: A callback function to call when an error is
                    found when processing the message; takes original\
                    SCPRequest, exception caught and a list of tuples of\
                    (filename, line number, function name, text) as a traceback
        """

        # Update the packet and store required details
        global _next_sequence
        request.scp_request_header.sequence = _next_sequence
        request_data = self._connection.get_scp_data(request)
        self._requests[_next_sequence] = request
        self._request_data[_next_sequence] = request_data
        self._retries[_next_sequence] = self._n_retries
        self._callbacks[_next_sequence] = callback
        self._error_callbacks[_next_sequence] = error_callback
        self._send_time[_next_sequence] = time.time()
        _next_sequence = (_next_sequence + 1) % MAX_SEQUENCE

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
            self._do_retrieve(self._intermediate_channel_waits, 0.1)

        # Send the request, keeping track of how many are sent
        # self._token_bucket.consume(284)
        self._connection.send(request_data)
        self._in_progress += 1

    def finish(self):
        """ Indicate the end of the packets to be sent.  This must be called\
            to ensure that all responses are received and handled.
        """
        while self._in_progress > 0:
            self._do_retrieve(0, self._packet_timeout)

    @property
    def n_timeouts(self):
        return self._n_timeouts

    @property
    def n_channels(self):
        return self._n_channels

    @property
    def n_resent(self):
        return self._n_resent

    @property
    def n_retry_code_resent(self):
        return self._n_retry_code_resent

    def _remove_record(self, seq):
        del self._send_time[seq]
        if seq in self._requests:
            del self._requests[seq]
        del self._request_data[seq]
        del self._retries[seq]
        del self._callbacks[seq]
        del self._error_callbacks[seq]

    def _single_retrieve(self, timeout):
        # Receive the next response
        result, seq, raw_data, offset = \
            self._connection.receive_scp_response(timeout)

        # Only process responses which have matching requests
        if seq in self._requests:
            request_sent = self._requests[seq]

            # If the response can be retried, retry it, as long as the
            # timeout hasn't expired

            if (result in self._retry_codes and
                    (time.time() - self._send_time[seq] <
                        self._packet_timeout)):
                self._connection.send(self._request_data[seq])
                self._n_retry_code_resent += 1
            else:

                # No retry is possible - try constructing the result
                try:
                    response = request_sent.get_scp_response()
                    response.read_bytestring(raw_data, offset)
                    if self._callbacks[seq] is not None:
                        self._callbacks[seq](response)
                except Exception as e:
                    self._error_callbacks[seq](
                        request_sent, e, sys.exc_info()[2])

                # Remove the sequence from the outstanding responses
                self._remove_record(seq)
                self._in_progress -= 1

    def _handle_receive_timeout(self, to_resend):
        self._n_timeouts += 1

        # If there is a timeout, all packets remaining are resent
        time_now = time.time()
        to_remove = list()
        for seq, request_sent in self._requests.iteritems():
            if time_now - self._send_time[seq] >= self._packet_timeout:
                to_resend.append((seq, request_sent))
                self._in_progress -= 1
                to_remove.append(seq)
        for seq in to_remove:
            del self._requests[seq]

    def _resend(self, seq, request_sent):
        if self._retries[seq] > 0:
            # If the request can be retried, retry it
            self._retries[seq] -= 1
            self._in_progress += 1
            self._requests[seq] = request_sent
            self._send_time[seq] = time.time()
            self._connection.send(self._request_data[seq])
            self._n_resent += 1
        else:
            # Otherwise, report it as a timeout
            raise SpinnmanTimeoutException(
                request_sent.scp_request_header.command, self._packet_timeout)

    def _do_retrieve(self, n_packets, timeout):
        """ Receives responses until there are only n_packets responses left

        :param n_packets: The number of packets that can remain after running
        """

        # Keep a set of packets to resend
        to_resend = list()

        # While there are still more packets in progress than some threshold
        while self._in_progress > n_packets:
            try:
                # Receive the next response
                self._single_retrieve(timeout)
            except SpinnmanTimeoutException:
                self._handle_receive_timeout(to_resend)

        # Try to resend the packets
        for seq, request_sent in to_resend:
            try:
                if self._retries[seq] > 0:
                    # If the request can be retried, retry it
                    self._retries[seq] -= 1
                    self._in_progress += 1
                    self._requests[seq] = request_sent
                    self._send_time[seq] = time.time()
                    self._connection.send(self._request_data[seq])
                    self._n_resent += 1
                else:
                    # Otherwise, report it as a timeout
                    raise SpinnmanTimeoutException(
                        request_sent.scp_request_header.command,
                        self._packet_timeout)
            except Exception as e:
                self._error_callbacks[seq](
                    request_sent, e, sys.exc_info()[2])
                self._remove_record(seq)
