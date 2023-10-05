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
from spinnman.messages.sdp import SDPMessage, SDPFlag
from .udp_connection import UDPConnection
from .utils import update_sdp_header_for_udp_send
from spinnman.connections.abstract_classes import Listenable

_TWO_SKIP = struct.Struct("<2x")


class SDPConnection(UDPConnection, Listenable):
    """
    A connection that talks SpiNNaker Datagram Protocol.
    """
    __slots__ = [
        "_chip_x",
        "_chip_y"]

    def __init__(self, chip_x=None, chip_y=None, local_host=None,
                 local_port=None, remote_host=None, remote_port=None):
        """
        :param int chip_x: The optional x-coordinate of the chip at the remote
            end of the connection. If not specified, it will not be possible
            to send SDP messages that require a response with this connection.
        :param int chip_y: The optional y-coordinate of the chip at the remote
            end of the connection. If not specified, it will not be possible
            to send SDP messages that require a response with this connection.
        :param str local_host: The optional IP address or host name of the
            local interface to listen on
        :param int local_port: The optional local port to listen on
        :param str remote_host: The optional remote host name or IP address to
            send messages to. If not specified, sending will not be possible
            using this connection
        :param int remote_port: The optional remote port number to send
            messages to. If not specified, sending will not be possible using
            this connection
        """
        # pylint: disable=too-many-arguments
        super().__init__(local_host, local_port, remote_host, remote_port)
        self._chip_x = chip_x
        self._chip_y = chip_y

    def receive_sdp_message(self, timeout=None):
        """
        Receives an SDP message from this connection.  Blocks until the
        message has been received, or a timeout occurs.

        :param int timeout:
            The time in seconds to wait for the message to arrive; if not
            specified, will wait forever, or until the connection is closed.
        :return: The received SDP message
        :rtype: SDPMessage
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

    def send_sdp_message(self, sdp_message):
        """
        Sends an SDP message down this connection.

        :param SDPMessage sdp_message: The SDP message to be sent
        :raise SpinnmanIOException:
            If there is an error sending the message.
        """
        # If a reply is expected, the connection should
        if sdp_message.sdp_header.flags == SDPFlag.REPLY_EXPECTED:
            update_sdp_header_for_udp_send(
                sdp_message.sdp_header, self._chip_x, self._chip_y)
        else:
            update_sdp_header_for_udp_send(sdp_message.sdp_header, 0, 0)
        self.send(_TWO_SKIP.pack() + sdp_message.bytestring)

    @overrides(Listenable.get_receive_method)
    def get_receive_method(self):
        return self.receive_sdp_message

    def __repr__(self):
        return (
            f"SDPConnection(chip_x={self._chip_x}, chip_y={self._chip_y}, "
            f"local_host={self.local_ip_address}, local_port={self.local_port}"
            f", remote_host={self.remote_ip_address}, "
            f"remote_port={self.remote_port})")
