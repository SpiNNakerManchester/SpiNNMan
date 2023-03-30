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
from .udp_connection import UDPConnection
from spinnman.connections.abstract_classes import Listenable
from spinnman.messages.eieio import (
    read_eieio_command_message, read_eieio_data_message)
from spinn_utilities.overrides import overrides

_ONE_SHORT = struct.Struct("<H")
_REPR_TEMPLATE = "EIEIOConnection(local_host={}, local_port={},"\
    "remote_host={}, remote_port={})"


class EIEIOConnection(UDPConnection, Listenable):
    """
    A UDP connection for sending and receiving raw EIEIO messages.
    """
    __slots__ = []

    def receive_eieio_message(self, timeout=None):
        """
        Receives an EIEIO message from this connection.  Blocks until
        a message has been received, or a timeout occurs.

        :param int timeout:
            The time in seconds to wait for the message to arrive; if not
            specified, will wait forever, or until the connection is closed
        :return: an EIEIO message
        :rtype: AbstractEIEIOMessage
        :raise SpinnmanIOException:
            If there is an error receiving the message.
        :raise SpinnmanTimeoutException:
            If there is a timeout before a message is received.
        :raise SpinnmanInvalidPacketException:
            If the received packet is not a valid EIEIO message.
        :raise SpinnmanInvalidParameterException:
            If one of the fields of the EIEIO message is invalid.
        """
        data = self.receive(timeout)
        header = _ONE_SHORT.unpack_from(data)[0]
        if header & 0xC000 == 0x4000:
            return read_eieio_command_message(data, 0)
        return read_eieio_data_message(data, 0)

    def send_eieio_message(self, eieio_message):
        """
        Sends an EIEIO message down this connection.

        :param AbstractEIEIOMessage eieio_message:
            The EIEIO message to be sent
        :raise SpinnmanIOException:
            If there is an error sending the message
        """
        self.send(eieio_message.bytestring)

    def send_eieio_message_to(self, eieio_message, ip_address, port):
        self.send_to(eieio_message.bytestring, (ip_address, port))

    @overrides(Listenable.get_receive_method)
    def get_receive_method(self):
        return self.receive_eieio_message

    def __repr__(self):
        return _REPR_TEMPLATE.format(
            self.local_ip_address, self.local_port,
            self.remote_ip_address, self.remote_port)
