# Copyright (c) 2017-2019 The University of Manchester
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import struct
from spinnman.constants import SCP_SCAMP_PORT
from spinnman.messages.scp.enums import SCPResult
from .utils import update_sdp_header_for_udp_send
from .sdp_connection import SDPConnection
from spinnman.connections.abstract_classes import SCPSender, SCPReceiver
from spinn_utilities.overrides import overrides

_TWO_SHORTS = struct.Struct("<2H")
_TWO_SKIP = struct.Struct("<2x")
_REPR_TEMPLATE = "SCAMPConnection(chip_x={}, chip_y={}, local_host={}," \
    " local_port={}, remote_host={}, remote_port={})"


class SCAMPConnection(SDPConnection, SCPSender, SCPReceiver):
    """ A UDP connection to SCAMP on the board.
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
    def chip_x(self):
        return self._chip_x

    @property
    def chip_y(self):
        return self._chip_y

    def update_chip_coordinates(self, x, y):
        self._chip_x = x
        self._chip_y = y

    @overrides(SCPSender.get_scp_data,
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

    @overrides(SCPReceiver.receive_scp_response)
    def receive_scp_response(self, timeout=1.0):
        data = self.receive(timeout)
        result, sequence = _TWO_SHORTS.unpack_from(data, 10)
        return SCPResult(result), sequence, data, 2

    def receive_scp_response_with_address(self, timeout=1.0):
        data, (addr, port) = self.receive_with_address(timeout)
        result, sequence = _TWO_SHORTS.unpack_from(data, 10)
        return SCPResult(result), sequence, data, 2, addr, port

    @overrides(SCPSender.send_scp_request)
    def send_scp_request(self, scp_request):
        self.send(self.get_scp_data(scp_request))

    def send_scp_request_to(self, scp_request, x, y, ip_address):
        self.send_to(
            self.get_scp_data(scp_request, x, y),
            (str(ip_address), SCP_SCAMP_PORT))

    def __repr__(self):
        return _REPR_TEMPLATE.format(
            self._chip_x, self._chip_y, self.local_ip_address,
            self.local_port, self.remote_ip_address, self.remote_port)
