# Copyright (c) 2017-2019 The University of Manchester
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
from .udp_connection import UDPConnection
from spinnman.connections.abstract_classes import (
    EIEIOReceiver, EIEIOSender, Listenable)
from spinnman.messages.eieio import (
    read_eieio_command_message, read_eieio_data_message)

_ONE_SHORT = struct.Struct("<H")
_REPR_TEMPLATE = "EIEIOConnection(local_host={}, local_port={},"\
    "remote_host={}, remote_port={})"


class EIEIOConnection(
        UDPConnection, EIEIOReceiver, EIEIOSender, Listenable):
    """ A UDP connection for sending and receiving raw EIEIO messages.
    """
    __slots__ = []

    def receive_eieio_message(self, timeout=None):
        data = self.receive(timeout)
        header = _ONE_SHORT.unpack_from(data)[0]
        if header & 0xC000 == 0x4000:
            return read_eieio_command_message(data, 0)
        return read_eieio_data_message(data, 0)

    def send_eieio_message(self, eieio_message):
        self.send(eieio_message.bytestring)

    def send_eieio_message_to(self, eieio_message, ip_address, port):
        self.send_to(eieio_message.bytestring, (ip_address, port))

    def get_receive_method(self):
        return self.receive_eieio_message

    def __repr__(self):
        return _REPR_TEMPLATE.format(
            self.local_ip_address, self.local_port,
            self.remote_ip_address, self.remote_port)
