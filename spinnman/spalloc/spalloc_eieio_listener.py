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
from typing import Optional, Tuple
from spinn_utilities.abstract_base import AbstractBase, abstractmethod
from spinn_utilities.overrides import overrides
from spinn_utilities.typing.coords import XY
from spinnman.connections.udp_packet_connections import EIEIOConnection
from spinnman.constants import SCP_SCAMP_PORT
from spinnman.exceptions import SpinnmanTimeoutException
from spinnman.messages.eieio import (
    AbstractEIEIOMessage,
    read_eieio_command_message, read_eieio_data_message)
from spinnman.messages.sdp import SDPMessage, SDPFlag, SDPHeader
from spinnman.messages.scp.impl import IPTagSet
from .spalloc_proxied_connection import SpallocProxiedConnection
# mypy: disable-error-code=empty-body

_ONE_SHORT = struct.Struct("<H")
_TWO_SHORTS = struct.Struct("<2H")
_TWO_SKIP: bytes = b'\0\0'
_NUM_UPDATE_TAG_TRIES = 3
_UPDATE_TAG_TIMEOUT = 1.0


class SpallocEIEIOListener(
        EIEIOConnection, SpallocProxiedConnection, metaclass=AbstractBase):
    """
    The socket interface supported by proxied EIEIO listener sockets.
    This emulates an :py:class:`EIEOConnection` opened with no address
    specified.
    """
    __slots__ = ()

    @overrides(EIEIOConnection.receive_eieio_message)
    def receive_eieio_message(
            self, timeout: Optional[float] = None) -> AbstractEIEIOMessage:
        data = self.receive(timeout)
        header = _ONE_SHORT.unpack_from(data)[0]
        if header & 0xC000 == 0x4000:
            return read_eieio_command_message(data, 0)
        return read_eieio_data_message(data, 0)

    @overrides(SpallocProxiedConnection.send)
    def send(self, data: bytes) -> None:
        """
        .. note::
            This class does not allow sending.
        """

    @abstractmethod
    def _get_chip_coords(self, ip_address: str) -> XY:
        """
        Get the coordinates of a chip given its IP address.

        :param ip_address:
            The IP address of an Ethernet-enabled chip in the job.
        :return: Ethernet-enabled chip coordinates: X, Y
        """
        raise NotImplementedError

    @abstractmethod
    def send_to_chip(self, message: bytes, x: int, y: int,
                     port: int = SCP_SCAMP_PORT) -> None:
        """
        Send a message on an open socket to a particular board.

        :param message: The message to send.
        :param x:
            The X coordinate of the Ethernet-enabled chip to send the message
            to.
        :param y:
            The Y coordinate of the Ethernet-enabled chip to send the message
            to.
        :param port:
            The UDP port on the Ethernet-enabled chip to send the message to.
            Defaults to the SCP port.
        """
        raise NotImplementedError

    def send_to(self, data: bytes, address: Tuple[str, int]) -> None:
        """
        Send a message on an open socket.

        :param data: The message to send.
        :param address:
            Where to send it to. Must be the address of an Ethernet-enabled
            chip on a board allocated to the job. Does not mean that SpiNNaker
            is listening on that port (but the SCP port is being listened to if
            the board is booted).
        """
        ip, port = address
        x, y = self._get_chip_coords(ip)
        self.send_to_chip(data, x, y, port)

    @property
    @abstractmethod
    def local_ip_address(self) -> str:  # type: ignore[override]
        """
        The IP address on the server to which the connection is bound.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def local_port(self) -> int:  # type: ignore[override]
        """
        The port on the server to which the connection is bound.
        """
        raise NotImplementedError

    def send_eieio_message_to_core(
            self, eieio_message: AbstractEIEIOMessage, x: int, y: int, p: int,
            ip_address: str) -> None:
        """
        Send an EIEIO message (one way) to a given core.

        :param eieio_message: The message to send.
        :param x: The X coordinate of the core to send to.
        :param y: The Y coordinate of the core to send to.
        :param p: The ID of the core to send to.
        :param ip_address:
            The IP address of the Ethernet-enabled chip to route the message
            via.
        """
        sdp_message = SDPMessage(
            SDPHeader(
                flags=SDPFlag.REPLY_NOT_EXPECTED, tag=0,
                destination_port=1, destination_cpu=p,
                destination_chip_x=x, destination_chip_y=y,
                source_port=0, source_cpu=0,
                source_chip_x=0, source_chip_y=0),
            data=eieio_message.bytestring)
        self.send_to(
            _TWO_SKIP + sdp_message.bytestring, (ip_address, SCP_SCAMP_PORT))

    def update_tag(
            self, x: int, y: int, tag: int, do_receive: bool = True) -> None:
        """
        Update the given tag on the given Ethernet-enabled chip to send
        messages to this connection.

        :param x: The Ethernet-enabled chip's X coordinate
        :param y: The Ethernet-enabled chip's Y coordinate
        :param tag: The tag ID to update
        :param do_receive: Whether to receive the response or not
        :raises SpinnmanTimeoutException:
            If the message isn't handled within a reasonable timeout.
        :raises SpinnmanUnexpectedResponseCodeException:
            If the message is rejected by SpiNNaker/SCAMP.
        """
        request = IPTagSet(
            x, y, [0, 0, 0, 0], 0, tag, strip=True, use_sender=True)
        request.sdp_header.flags = SDPFlag.REPLY_EXPECTED_NO_P2P
        request.sdp_header.update_for_send(x, y)
        data = _TWO_SKIP + request.bytestring
        for _try in range(_NUM_UPDATE_TAG_TRIES):
            try:
                self.send_to_chip(data, x, y, SCP_SCAMP_PORT)
                if do_receive:
                    response_data = self.receive(_UPDATE_TAG_TIMEOUT)
                    request.get_scp_response().read_bytestring(
                        response_data, len(_TWO_SKIP))
                return
            except SpinnmanTimeoutException as e:
                if _try + 1 == _NUM_UPDATE_TAG_TRIES:
                    raise e

    def update_tag_by_ip(self, ip_address: str, tag: int) -> None:
        """
        Update a tag on a board at a given IP address to send messages to this
        connection.

        :param ip_address: The address of the Ethernet-enabled chip
        :param tag: The ID of the tag
        """
        x, y = self._get_chip_coords(ip_address)
        self.update_tag(x, y, tag)
