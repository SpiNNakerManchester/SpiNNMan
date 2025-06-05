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
from typing import Optional, Sequence, Tuple

from spinn_utilities.overrides import overrides

from spinnman.constants import SCP_SCAMP_PORT
from spinnman.messages.scp.enums import SCPResult
from spinnman.messages.scp.abstract_messages import AbstractSCPRequest
from spinnman.connections.abstract_classes import AbstractSCPConnection
from spinnman.model import BMPConnectionData

from .udp_connection import UDPConnection

_TWO_SHORTS = struct.Struct("<2H")
_TWO_SKIP = struct.Struct("<2x")


class BMPConnection(UDPConnection, AbstractSCPConnection):
    """
    A BMP connection which supports queries to the BMP of a SpiNNaker machine.
    """
    __slots__ = ("_boards", )

    def __init__(self, connection_data: BMPConnectionData):
        """
        :param connection_data:
            The description of what to connect to.
        """
        port = SCP_SCAMP_PORT if connection_data.port_num is None\
            else connection_data.port_num
        super().__init__(
            remote_host=connection_data.ip_address, remote_port=port)
        self._boards = connection_data.boards

    @property
    def boards(self) -> Sequence[int]:
        """
        The set of boards supported by the BMP.
        """
        return self._boards

    @property
    @overrides(AbstractSCPConnection.chip_x, extend_doc=False)
    def chip_x(self) -> int:
        """
        Defined to satisfy the AbstractSCPConnection - always 0 for a BMP.
        """
        return 0

    @property
    @overrides(AbstractSCPConnection.chip_y, extend_doc=False)
    def chip_y(self) -> int:
        """
        Defined to satisfy the AbstractSCPConnection - always 0 for a BMP.
        """
        return 0

    @overrides(AbstractSCPConnection.get_scp_data)
    def get_scp_data(self, scp_request: AbstractSCPRequest) -> bytes:
        scp_request.sdp_header.update_for_send(0, 0)
        return _TWO_SKIP.pack() + scp_request.bytestring

    @overrides(AbstractSCPConnection.receive_scp_response)
    def receive_scp_response(self, timeout: Optional[float] = 1.0) -> Tuple[
            SCPResult, int, bytes, int]:
        data = self.receive(timeout)
        result, sequence = _TWO_SHORTS.unpack_from(data, 10)
        return SCPResult(result), sequence, data, 2

    def __repr__(self) -> str:
        return (
            f"BMPConnection("
            f"boards={self._boards}, local_host={self.local_ip_address}, "
            f"local_port={self.local_port}, "
            f"remote_host={self.remote_ip_address}, "
            f"remote_port={self.remote_port})")
