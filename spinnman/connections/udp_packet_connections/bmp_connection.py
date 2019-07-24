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
from spinn_utilities.overrides import overrides
from .udp_connection import UDPConnection
from .utils import update_sdp_header_for_udp_send
from spinnman.constants import SCP_SCAMP_PORT
from spinnman.messages.scp.enums import SCPResult
from spinnman.connections.abstract_classes import SCPReceiver, SCPSender

_TWO_SHORTS = struct.Struct("<2H")
_TWO_SKIP = struct.Struct("<2x")
_REPR_TEMPLATE = "BMPConnection(cabinet={}, frame={}, boards={}, " \
    "local_host={}, local_port={}, remote_host={}, remote_port={}"


class BMPConnection(UDPConnection, SCPReceiver, SCPSender):
    """ A BMP connection which supports queries to the BMP of a SpiNNaker\
        machine
    """
    __slots__ = [
        "_boards",
        "_cabinet",
        "_frame"]

    def __init__(self, connection_data):
        """
        :param connection_data: The description of what to connect to.
        :type connection_data: \
            :py:class:`spinnman.model.bmp_connection_data.BMPConnectionData`
        """
        port = SCP_SCAMP_PORT if connection_data.port_num is None\
            else connection_data.port_num
        super(BMPConnection, self).__init__(
            remote_host=connection_data.ip_address, remote_port=port)
        self._cabinet = connection_data.cabinet
        self._frame = connection_data.frame
        self._boards = connection_data.boards

    @property
    def cabinet(self):
        """ The cabinet ID of the BMP

        :rtype: int
        """
        return self._cabinet

    @property
    def frame(self):
        """ The frame ID of the BMP

        :rtype: int
        """
        return self._frame

    @property
    def boards(self):
        """ The set of boards supported by the BMP

        :rtype: iterable of int
        """
        return self._boards

    @property
    def chip_x(self):
        """ Defined to satisfy the SCPSender - always 0 for a BMP
        """
        return 0

    @property
    def chip_y(self):
        """ Defined to satisfy the SCPSender - always 0 for a BMP
        """
        return 0

    @overrides(SCPSender.get_scp_data)
    def get_scp_data(self, scp_request):
        update_sdp_header_for_udp_send(scp_request.sdp_header, 0, 0)
        return _TWO_SKIP.pack() + scp_request.bytestring

    @overrides(SCPReceiver.receive_scp_response)
    def receive_scp_response(self, timeout=1.0):
        data = self.receive(timeout)
        result, sequence = _TWO_SHORTS.unpack_from(data, 10)
        return SCPResult(result), sequence, data, 2

    @overrides(SCPSender.send_scp_request)
    def send_scp_request(self, scp_request):
        self.send(self.get_scp_data(scp_request))

    def __repr__(self):
        return _REPR_TEMPLATE.format(
            self._cabinet, self._frame, self._boards,
            self.local_ip_address, self.local_port, self.remote_ip_address,
            self.remote_port)
