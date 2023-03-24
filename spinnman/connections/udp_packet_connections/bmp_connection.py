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
from spinn_utilities.overrides import overrides
from .udp_connection import UDPConnection
from spinnman.constants import SCP_SCAMP_PORT
from spinnman.messages.scp.enums import SCPResult
from spinnman.connections.abstract_classes import AbstractSCPConnection
from .utils import update_sdp_header_for_udp_send

_TWO_SHORTS = struct.Struct("<2H")
_TWO_SKIP = struct.Struct("<2x")


class BMPConnection(UDPConnection, AbstractSCPConnection):
    """
    A BMP connection which supports queries to the BMP of a SpiNNaker machine.
    """
    __slots__ = [
        "_boards",
        "_cabinet",
        "_frame"]

    def __init__(self, connection_data):
        """
        :param BMPConnectionData connection_data:
            The description of what to connect to.
        """
        port = SCP_SCAMP_PORT if connection_data.port_num is None\
            else connection_data.port_num
        super().__init__(
            remote_host=connection_data.ip_address, remote_port=port)
        self._cabinet = connection_data.cabinet
        self._frame = connection_data.frame
        self._boards = connection_data.boards

    @property
    def cabinet(self):
        """
        The cabinet ID of the BMP.

        :rtype: int
        """
        return self._cabinet

    @property
    def frame(self):
        """
        The frame ID of the BMP.

        :rtype: int
        """
        return self._frame

    @property
    def boards(self):
        """
        The set of boards supported by the BMP.

        :rtype: iterable(int)
        """
        return self._boards

    @property
    @overrides(AbstractSCPConnection.chip_x, extend_doc=False)
    def chip_x(self):
        """
        Defined to satisfy the AbstractSCPConnection - always 0 for a BMP.
        """
        return 0

    @property
    @overrides(AbstractSCPConnection.chip_y, extend_doc=False)
    def chip_y(self):
        """
        Defined to satisfy the AbstractSCPConnection - always 0 for a BMP.
        """
        return 0

    @overrides(AbstractSCPConnection.get_scp_data)
    def get_scp_data(self, scp_request):
        update_sdp_header_for_udp_send(scp_request.sdp_header, 0, 0)
        return _TWO_SKIP.pack() + scp_request.bytestring

    @overrides(AbstractSCPConnection.receive_scp_response)
    def receive_scp_response(self, timeout=1.0):
        data = self.receive(timeout)
        result, sequence = _TWO_SHORTS.unpack_from(data, 10)
        return SCPResult(result), sequence, data, 2

    @overrides(AbstractSCPConnection.send_scp_request)
    def send_scp_request(self, scp_request):
        self.send(self.get_scp_data(scp_request))

    def __repr__(self):
        return (
            f"BMPConnection(cabinet={self._cabinet}, frame={self._frame}, "
            f"boards={self._boards}, local_host={self.local_ip_address}, "
            f"local_port={self.local_port}, "
            f"remote_host={self.remote_ip_address}, "
            f"remote_port={self.remote_port})")
