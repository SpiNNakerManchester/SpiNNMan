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
"""
API of the client for the Spalloc web service.
"""

import struct
from typing import Tuple
from spinn_utilities.abstract_base import (
    AbstractBase, abstractproperty)
from spinn_utilities.overrides import overrides
from spinnman.connections.abstract_classes import Listenable
from spinnman.connections.udp_packet_connections import (
    update_sdp_header_for_udp_send, EIEIOConnection)
from spinnman.exceptions import SpinnmanTimeoutException
from spinnman.messages.eieio import (
    AbstractEIEIOMessage,
    read_eieio_command_message, read_eieio_data_message)
from spinnman.messages.sdp import SDPMessage, SDPFlag, SDPHeader
from spinnman.messages.scp.impl import IPTagSet
from .spalloc_proxied_connection import SpallocProxiedConnection

_ONE_SHORT = struct.Struct("<H")
_TWO_SKIP: bytes = b'\0\0'
_NUM_UPDATE_TAG_TRIES = 3
_UPDATE_TAG_TIMEOUT = 1.0


class SpallocEIEIOConnection(
        EIEIOConnection, SpallocProxiedConnection, metaclass=AbstractBase):
    """
    The socket interface supported by proxied EIEIO connected sockets.
    This emulates an :py:class:`EIEOConnection` opened with a remote address
    specified.
    """
    __slots__ = ()

    @overrides(EIEIOConnection.send_eieio_message)
    def send_eieio_message(self, eieio_message):
        # Not normally used, as packets need headers to go to SpiNNaker
        self.send(eieio_message.bytestring)

    def send_eieio_message_to_core(
            self, eieio_message: AbstractEIEIOMessage, x: int, y: int, p: int):
        sdp_message = SDPMessage(
            SDPHeader(
                flags=SDPFlag.REPLY_NOT_EXPECTED, tag=0,
                destination_port=1, destination_cpu=p,
                destination_chip_x=x, destination_chip_y=y,
                source_port=0, source_cpu=0,
                source_chip_x=0, source_chip_y=0),
            data=eieio_message.bytestring)
        self.send(_TWO_SKIP + sdp_message.bytestring)

    @overrides(EIEIOConnection.receive_eieio_message)
    def receive_eieio_message(self, timeout=None):
        data = self.receive(timeout)
        header = _ONE_SHORT.unpack_from(data)[0]
        if header & 0xC000 == 0x4000:
            return read_eieio_command_message(data, 0)
        return read_eieio_data_message(data, 0)

    @overrides(Listenable.get_receive_method)
    def get_receive_method(self):
        return self.receive_eieio_message

    @abstractproperty
    def _coords(self) -> Tuple[int, int]:
        """
        The X, Y coordinates of the chip this connection is connected to.

        :rtype: tuple(int,int)
        """

    def update_tag(self, tag: int, do_receive: bool = True):
        """
        Update the given tag on the connected Ethernet-enabled chip to send
        messages to this connection.

        :param int tag: The tag ID to update
        :param bool do_receive:
            Whether to do the reception of the response or not
        :raises SpinnmanTimeoutException:
            If the message isn't handled within a reasonable timeout.
        :raises SpinnmanUnexpectedResponseCodeException:
            If the message is rejected by SpiNNaker/SCAMP.
        """
        x, y = self._coords
        request = IPTagSet(
            x, y, [0, 0, 0, 0], 0, tag, strip=True, use_sender=True)
        request.sdp_header.flags = SDPFlag.REPLY_EXPECTED_NO_P2P
        update_sdp_header_for_udp_send(request.sdp_header, x, y)
        data = _TWO_SKIP + request.bytestring
        for _try in range(_NUM_UPDATE_TAG_TRIES):
            try:
                self.send(data)
                if do_receive:
                    response_data = self.receive(_UPDATE_TAG_TIMEOUT)
                    request.get_scp_response().read_bytestring(
                        response_data, len(_TWO_SKIP))
                return
            except SpinnmanTimeoutException as e:
                if _try + 1 == _NUM_UPDATE_TAG_TRIES:
                    raise e
