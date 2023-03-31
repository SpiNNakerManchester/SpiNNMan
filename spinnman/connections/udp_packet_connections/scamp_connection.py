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

import struct
from spinnman.constants import SCP_SCAMP_PORT
from spinnman.messages.scp.enums import SCPResult
from .sdp_connection import SDPConnection
from .utils import update_sdp_header_for_udp_send
from spinnman.connections.abstract_classes import AbstractSCPConnection
from spinn_utilities.overrides import overrides

_TWO_SHORTS = struct.Struct("<2H")
_TWO_SKIP = struct.Struct("<2x")


class SCAMPConnection(SDPConnection, AbstractSCPConnection):
    """
    A UDP connection to SCAMP on the board.
    """
    __slots__ = []

    def __init__(
            self, chip_x=255, chip_y=255, local_host=None, local_port=None,
            remote_host=None, remote_port=None):
        """
        :param int chip_x:
            The x-coordinate of the chip on the board with this remote_host
        :param int chip_y:
            The y-coordinate of the chip on the board with this remote_host
        :param str local_host: The optional IP address or host name of the
            local interface to listen on
        :param int local_port: The optional local port to listen on
        :param str remote_host: The optional remote host name or IP address to
            send messages to.  If not specified, sending will not be possible
            using this connection
        :param int remote_port: The optional remote port number to send
            messages to. If not specified, sending will not be possible using
            this connection
        """
        # pylint: disable=too-many-arguments
        if remote_port is None:
            remote_port = SCP_SCAMP_PORT
        super().__init__(
            chip_x, chip_y, local_host, local_port, remote_host, remote_port)

    @property
    @overrides(AbstractSCPConnection.chip_x)
    def chip_x(self):
        return self._chip_x

    @property
    @overrides(AbstractSCPConnection.chip_y)
    def chip_y(self):
        return self._chip_y

    def update_chip_coordinates(self, x, y):
        self._chip_x = x
        self._chip_y = y

    @overrides(AbstractSCPConnection.get_scp_data,
               additional_arguments=['x', 'y'], extend_defaults=True)
    def get_scp_data(self, scp_request, x=None, y=None):
        """
        :param int x: Optional: x-coordinate of where to send to
        :param int y: Optional: y-coordinate of where to send to
        """
        # pylint: disable=arguments-differ
        if x is None:
            x = self._chip_x
        if y is None:
            y = self._chip_y
        update_sdp_header_for_udp_send(scp_request.sdp_header, x, y)
        return _TWO_SKIP.pack() + scp_request.bytestring

    @overrides(AbstractSCPConnection.receive_scp_response)
    def receive_scp_response(self, timeout=1.0):
        data = self.receive(timeout)
        result, sequence = _TWO_SHORTS.unpack_from(data, 10)
        return SCPResult(result), sequence, data, 2

    def receive_scp_response_with_address(self, timeout=1.0):
        data, (addr, port) = self.receive_with_address(timeout)
        result, sequence = _TWO_SHORTS.unpack_from(data, 10)
        return SCPResult(result), sequence, data, 2, addr, port

    @overrides(AbstractSCPConnection.send_scp_request)
    def send_scp_request(self, scp_request):
        self.send(self.get_scp_data(scp_request))

    def send_scp_request_to(self, scp_request, x, y, ip_address):
        self.send_to(
            self.get_scp_data(scp_request, x, y),
            (str(ip_address), SCP_SCAMP_PORT))

    def __repr__(self):
        return (
            f"SCAMPConnection(chip_x={self._chip_x}, chip_y={self._chip_y}, "
            f"local_host={self.local_ip_address}, local_port={self.local_port}"
            f", remote_host={self.remote_ip_address}, "
            f"remote_port={self.remote_port})")
