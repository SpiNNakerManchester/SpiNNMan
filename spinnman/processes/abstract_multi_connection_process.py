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

import contextlib
import logging
import sys
from types import TracebackType
from typing import (
    Callable, Dict, Generator, Generic, List, Optional, TypeVar, cast)
from typing_extensions import Self, TypeAlias
from spinn_utilities.log import FormatAdapter
from spinnman.connections import SCPRequestPipeLine
from spinnman.constants import SCP_TIMEOUT, N_RETRIES
from spinnman.exceptions import (
    SpinnmanGenericProcessException, SpinnmanGroupedProcessException)
from .abstract_multi_connection_process_connection_selector import (
    AbstractMultiConnectionProcessConnectionSelector)
from spinnman.connections.udp_packet_connections import SCAMPConnection
from spinnman.messages.scp.abstract_messages import (
    AbstractSCPRequest, AbstractSCPResponse)
_R = TypeVar("_R", bound=AbstractSCPResponse)
_ECB: TypeAlias = Callable[
    [AbstractSCPRequest[_R], Exception, TracebackType, SCAMPConnection], None]

logger = FormatAdapter(logging.getLogger(__name__))


class AbstractMultiConnectionProcess(Generic[_R]):
    """
    A process for talking to SpiNNaker efficiently that uses multiple
    connections in communication if relevant.
    """
    __slots__ = (
        "_error_requests",
        "_exceptions",
        "_tracebacks",
        "_connections",
        "_intermediate_channel_waits",
        "_n_channels",
        "_n_retries",
        "_conn_selector",
        "_scp_request_pipelines",
        "_timeout")

    def __init__(self, next_connection_selector:
                 AbstractMultiConnectionProcessConnectionSelector,
                 n_retries: int = N_RETRIES, timeout: float = SCP_TIMEOUT,
                 n_channels: int = 8, intermediate_channel_waits: int = 7):
        """
        :param next_connection_selector:
            How to choose the connection.
        :type next_connection_selector:
            AbstractMultiConnectionProcessConnectionSelector
        :param int n_retries:
            The number of retries of a message to use. Passed to
            :py:class:`SCPRequestPipeLine`
        :param float timeout:
            The timeout, in seconds. Passed to :py:class:`SCPRequestPipeLine`
        :param int n_channels:
            The maximum number of channels to use when talking to a particular
            SCAMP instance. Passed to :py:class:`SCPRequestPipeLine`
        :param int intermediate_channel_waits:
            The maximum number of outstanding message/reply pairs to have on a
            particular connection. Passed to :py:class:`SCPRequestPipeLine`
        """
        self._exceptions: List[Exception] = []
        self._tracebacks: List[TracebackType] = []
        self._error_requests: List[AbstractSCPRequest[_R]] = []
        self._connections: List[SCAMPConnection] = []
        self._scp_request_pipelines: Dict[
            SCAMPConnection, SCPRequestPipeLine[_R]] = dict()
        self._n_retries = n_retries
        self._timeout = timeout
        self._n_channels = n_channels
        self._intermediate_channel_waits = intermediate_channel_waits
        self._conn_selector = next_connection_selector

    def _send_request(self, request: AbstractSCPRequest[_R],
                      callback: Optional[Callable[[_R], None]] = None,
                      error_callback: Optional[_ECB] = None):
        if error_callback is None:
            error_callback = self._receive_error
        connection = self._conn_selector.get_next_connection(request)
        if connection not in self._scp_request_pipelines:
            self._scp_request_pipelines[connection] = SCPRequestPipeLine(
                connection, n_retries=self._n_retries,
                packet_timeout=self._timeout,
                n_channels=self._n_channels,
                intermediate_channel_waits=self._intermediate_channel_waits)
        self._scp_request_pipelines[connection].send_request(
            request, callback, error_callback)

    def _receive_error(
            self, request: AbstractSCPRequest[_R], exception: Exception,
            tb: TracebackType, connection: SCAMPConnection):
        self._error_requests.append(request)
        self._exceptions.append(exception)
        self._tracebacks.append(tb)
        self._connections.append(connection)

    def is_error(self) -> bool:
        return bool(self._exceptions)

    def _finish(self) -> None:
        for request_pipeline in self._scp_request_pipelines.values():
            request_pipeline.finish()

    @contextlib.contextmanager
    def _collect_responses(
            self, *, print_exception: bool = False,
            check_error: bool = True) -> Generator[Self, None, None]:
        """
        A simple context for calls. Lets you do this::

            with self._collect_responses():
                self._send_request(...)

        instead of this::

            self._send_request(...)
            self._finish()
            self.check_for_error()

        :param bool print_exception:
            Whether to log errors as well as raising
        :param bool check_error:
            Whether to check for errors; if not, caller must handle
        """
        yield self
        for request_pipeline in self._scp_request_pipelines.values():
            request_pipeline.finish()
        if check_error and self._exceptions:
            self.check_for_error(print_exception=print_exception)

    @property
    def connection_selector(
            self) -> AbstractMultiConnectionProcessConnectionSelector:
        """
        The connection selector of the process.

        :rtype: AbstractMultiConnectionProcessConnectionSelector
        """
        return self._conn_selector

    def check_for_error(self, print_exception: bool = False):
        if len(self._exceptions) == 1:
            exc_info = sys.exc_info()
            sdp_header = self._error_requests[0].sdp_header
            phys_p = sdp_header.get_physical_cpu_id()

            if print_exception:
                connection = self._connections[0]
                logger.error(
                    "failure in request to board {} with ethernet chip "
                    "({}, {}) for chip ({}, {}, {}({}))",
                    connection.remote_ip_address, connection.chip_x,
                    connection.chip_y, sdp_header.destination_chip_x,
                    sdp_header.destination_chip_y, sdp_header.destination_cpu,
                    phys_p)

            raise SpinnmanGenericProcessException(
                self._exceptions[0], cast(TracebackType, exc_info[2]),
                sdp_header.destination_chip_x,
                sdp_header.destination_chip_y, sdp_header.destination_cpu,
                phys_p, self._tracebacks[0])
        elif self._exceptions:
            ex = SpinnmanGroupedProcessException(
                self._error_requests, self._exceptions, self._tracebacks,
                self._connections)
            if print_exception:
                logger.error("{}", str(ex))
            raise ex
