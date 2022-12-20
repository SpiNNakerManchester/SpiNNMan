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
"""
API of the client for the Spalloc web service.
"""

import struct
from typing import Tuple
from spinn_utilities.abstract_base import (
    AbstractBase, abstractmethod, abstractproperty)
from spinn_utilities.overrides import overrides
from spinnman.connections.abstract_classes import Listenable
from spinnman.connections.udp_packet_connections import (
    update_sdp_header_for_udp_send, EIEIOConnection)
from spinnman.constants import SCP_SCAMP_PORT
from spinnman.exceptions import SpinnmanTimeoutException
from spinnman.messages.eieio import (
    AbstractEIEIOMessage,
    read_eieio_command_message, read_eieio_data_message)
from spinnman.messages.sdp import SDPMessage, SDPFlag, SDPHeader
from spinnman.messages.scp.impl import IPTagSet
from .spalloc_proxied_connection import SpallocProxiedConnection

_ONE_SHORT = struct.Struct("<H")
_TWO_SHORTS = struct.Struct("<2H")
_TWO_SKIP: bytes = b'\0\0'
_NUM_UPDATE_TAG_TRIES = 3
_UPDATE_TAG_TIMEOUT = 1.0


class SpallocEIEIOListener(
        EIEIOConnection, SpallocProxiedConnection, metaclass=AbstractBase):
    """
    The socket interface supported by proxied EIEIO listener sockets.
    This emulates an EIEOConnection opened with no address specified.
    """
    __slots__ = ()

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

    @overrides(SpallocProxiedConnection.send)
    def send(self, data):
        """
        .. note::
            This class does not allow sending.
        """

    @abstractmethod
    def _get_chip_coords(self, ip_address: str) -> Tuple[int, int]:
        """
        Get the coordinates of a chip given its IP address.

        :param str ip_address: The IP address of an ethernet chip in the job.
        :return: Ethernet chip coordinates: X, Y
        :rtype: tuple(int, int)
        """

    @abstractmethod
    def send_to_chip(
            self, message: bytes, x: int, y: int, port: int = SCP_SCAMP_PORT):
        """
        Send a message on an open socket to a particular board.

        :param bytes message: The message to send.
        :param int x:
            The X coordinate of the ethernet chip to send the message to.
        :param int y:
            The Y coordinate of the ethernet chip to send the message to.
        :param int port:
            The UDP port on the ethernet chip to send the message to.
            Defaults to the SCP port.
        """

    def send_to(self, data: bytes, address: Tuple[str, int]):
        """
        Send a message on an open socket.

        :param bytes message: The message to send.
        :param tuple(str,int) address:
            Where to send it to. Must be the address of an ethernet chip on a
            board allocated to the job. Does not mean that SpiNNaker is
            listening on that port (but the SCP port is being listened to if
            the board is booted).
        """
        ip, port = address
        x, y = self._get_chip_coords(ip)
        self.send_to_chip(data, x, y, port)

    @abstractproperty
    def local_ip_address(self) -> str:
        """ The IP address on the server to which the connection is bound.

        :return: The IP address as a dotted string, e.g., 0.0.0.0
        :rtype: str
        """

    @abstractproperty
    def local_port(self) -> int:
        """ The port on the server to which the connection is bound.

        :return: The local port number
        :rtype: int
        """

    def send_eieio_message_to_core(
            self, eieio_message: AbstractEIEIOMessage, x: int, y: int, p: int,
            ip_address: str):
        """
        Send an EIEIO message (one way) to a given core.

        :param AbstractEIEIOMessage eieio_message:
            The message to send.
        :param int x:
            The X coordinate of the core to send to.
        :param int y:
            The Y coordinate of the core to send to.
        :param int p:
            The ID of the core to send to.
        :param str ip_address:
            The IP address of the ethernet chip to route the message via.
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

    def update_tag(self, x: int, y: int, tag: int):
        """
        Update the given tag on the given ethernet chip to send messages to
        this connection.

        :param int x: The ethernet chip's X coordinate
        :param int y: The ethernet chip's Y coordinate
        :param int tag: The tag ID to update
        :raises SpinnmanTimeoutException:
            If the message isn't handled within a reasonable timeout.
        :raises SpinnmanUnexpectedResponseCodeException:
            If the message is rejected by SpiNNaker/SCAMP.
        """
        request = IPTagSet(
            x, y, [0, 0, 0, 0], 0, tag, strip=True, use_sender=True)
        request.sdp_header.flags = SDPFlag.REPLY_EXPECTED_NO_P2P
        update_sdp_header_for_udp_send(request.sdp_header, x, y)
        data = _TWO_SKIP + request.bytestring
        for _try in range(_NUM_UPDATE_TAG_TRIES):
            try:
                self.send_to_chip(data, x, y, SCP_SCAMP_PORT)
                response_data = self.receive(_UPDATE_TAG_TIMEOUT)
                request.get_scp_response().read_bytestring(
                    response_data, len(_TWO_SKIP))
                return
            except SpinnmanTimeoutException as e:
                if _try + 1 == _NUM_UPDATE_TAG_TRIES:
                    raise e

    def update_tag_by_ip(self, ip_address: str, tag: int):
        """
        Update a tag on a board at a given IP address to send messages to this
        connection.

        :param str ip_address: The address of the ethernet chip
        :param int tag: The ID of the tag
        """
        x, y = self._get_chip_coords(ip_address)
        self.update_tag(x, y, tag)
