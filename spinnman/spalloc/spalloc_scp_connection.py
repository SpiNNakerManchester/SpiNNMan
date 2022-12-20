# Copyright (c) 2022 The University of Manchester
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
from typing import Callable, Tuple
from spinn_utilities.abstract_base import AbstractBase
from spinn_utilities.overrides import overrides
from spinnman.connections.abstract_classes import Listenable
from spinnman.connections.udp_packet_connections import (
    update_sdp_header_for_udp_send, SCAMPConnection)
from spinnman.messages.sdp import SDPMessage, SDPFlag
from spinnman.messages.scp.abstract_messages import AbstractSCPRequest
from spinnman.messages.scp.enums import SCPResult
from .spalloc_proxied_connection import SpallocProxiedConnection

_TWO_SHORTS = struct.Struct("<2H")
_TWO_SKIP: bytes = b'\0\0'


class SpallocSCPConnection(
        SCAMPConnection, SpallocProxiedConnection,
        metaclass=AbstractBase):
    """
    The socket interface supported by proxied sockets. The socket will always
    be talking to a specific board. This emulates a SCAMPConnection.
    """
    __slots__ = ()

    def __init__(self, x, y):
        super(SpallocSCPConnection, self).__init__(x, y)

    @overrides(Listenable.get_receive_method)
    def get_receive_method(self) -> Callable:
        return self.receive_sdp_message

    @overrides(SCAMPConnection.receive_sdp_message)
    def receive_sdp_message(self, timeout=None) -> SDPMessage:
        data = self.receive(timeout)
        return SDPMessage.from_bytestring(data, 2)

    @overrides(SCAMPConnection.send_sdp_message)
    def send_sdp_message(self, sdp_message: SDPMessage):
        # If a reply is expected, the connection should
        if sdp_message.sdp_header.flags == SDPFlag.REPLY_EXPECTED:
            update_sdp_header_for_udp_send(
                sdp_message.sdp_header, self.chip_x, self.chip_y)
        else:
            update_sdp_header_for_udp_send(sdp_message.sdp_header, 0, 0)
        self.send(_TWO_SKIP + sdp_message.bytestring)

    @overrides(SCAMPConnection.receive_scp_response)
    def receive_scp_response(
            self, timeout=1.0) -> Tuple[SCPResult, int, bytes, int]:
        data = self.receive(timeout)
        result, sequence = _TWO_SHORTS.unpack_from(data, 10)
        return SCPResult(result), sequence, data, 2

    @overrides(SCAMPConnection.send_scp_request)
    def send_scp_request(self, scp_request: AbstractSCPRequest):
        self.send(self.get_scp_data(scp_request))

    @overrides(SCAMPConnection.get_scp_data)
    def get_scp_data(
            self, scp_request: AbstractSCPRequest, x=None, y=None) -> bytes:
        if x is None:
            x = self.chip_x
        if y is None:
            y = self.chip_y
        update_sdp_header_for_udp_send(scp_request.sdp_header, x, y)
        return _TWO_SKIP + scp_request.bytestring
