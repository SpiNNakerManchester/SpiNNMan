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
from typing import Callable, Optional

from spinn_utilities.overrides import overrides
from spinnman.messages.sdp import SDPMessage, SDPFlag
from spinnman.connections.abstract_classes import Listenable
from spinnman.exceptions import SpinnmanUnsupportedOperationException

from .udp_connection import UDPConnection

_TWO_SKIP = struct.Struct("<2x")


class SDPConnection(UDPConnection, Listenable[SDPMessage]):
    """
    A connection that talks SpiNNaker Datagram Protocol.
    """
    __slots__ = (
        "_chip_x",
        "_chip_y")

    def __init__(
            self, chip_x: int, chip_y: int,
            local_host: Optional[str] = None,
            local_port: Optional[int] = None,
            remote_host: Optional[str] = None,
            remote_port: Optional[int] = None):
        """
        :param chip_x: The optional x-coordinate of the chip at the remote
            end of the connection. If not specified, it will not be possible
            to send SDP messages that require a response with this connection.
        :param chip_y: The optional y-coordinate of the chip at the remote
            end of the connection. If not specified, it will not be possible
            to send SDP messages that require a response with this connection.
        :param local_host: The optional IP address or host name of the
            local interface to listen on
        :param local_port: The optional local port to listen on
        :param remote_host: The optional remote host name or IP address to
            send messages to. If not specified, sending will not be possible
            using this connection
        :param remote_port: The optional remote port number to send
            messages to. If not specified, sending will not be possible using
            this connection
        """
        super().__init__(local_host, local_port, remote_host, remote_port)
        self._chip_x = chip_x
        self._chip_y = chip_y

    def receive_sdp_message(
            self, timeout: Optional[float] = None) -> SDPMessage:
        """
        Receives an SDP message from this connection.  Blocks until the
        message has been received, or a timeout occurs.

        :param timeout:
            The time in seconds to wait for the message to arrive; if not
            specified, will wait forever, or until the connection is closed.
        :return: The received SDP message
        :raise SpinnmanIOException:
            If there is an error receiving the message
        :raise SpinnmanTimeoutException:
            If there is a timeout before a message is received
        :raise SpinnmanInvalidPacketException:
            If the received packet is not a valid SDP message
        :raise SpinnmanInvalidParameterException:
            If one of the fields of the SDP message is invalid
        """
        data = self.receive(timeout)
        return SDPMessage.from_bytestring(data, 2)

    def send_sdp_message(self, sdp_message: SDPMessage) -> None:
        """
        Sends an SDP message down this connection.

        :param sdp_message: The SDP message to be sent
        :raise SpinnmanIOException:
            If there is an error sending the message.
        """
        if self._chip_x is None or self._chip_y is None:
            raise SpinnmanUnsupportedOperationException(
                "send on receive-only connection")
        # If a reply is expected, the connection should
        if sdp_message.sdp_header.flags == SDPFlag.REPLY_EXPECTED:
            sdp_message.sdp_header.update_for_send(self._chip_x, self._chip_y)
        else:
            sdp_message.sdp_header.update_for_send(0, 0)
        self.send(_TWO_SKIP.pack() + sdp_message.bytestring)

    @overrides(Listenable.get_receive_method)
    def get_receive_method(  # type: ignore[override]
            self) -> Callable[[], SDPMessage]:
        return self.receive_sdp_message

    def __repr__(self) -> str:
        return (
            f"SDPConnection(chip_x={self._chip_x}, chip_y={self._chip_y}, "
            f"local_host={self.local_ip_address}, local_port={self.local_port}"
            f", remote_host={self.remote_ip_address}, "
            f"remote_port={self.remote_port})")
