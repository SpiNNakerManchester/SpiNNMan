# Copyright (c) 2022 The University of Manchester
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
    be talking to a specific board. This emulates a
    :py:class:`SCAMPConnection`.
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
