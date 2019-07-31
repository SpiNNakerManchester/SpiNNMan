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
from .eieio_command_message import EIEIOCommandMessage
from .eieio_command_header import EIEIOCommandHeader
from spinnman.constants import EIEIO_COMMAND_IDS

_PATTERN_B = struct.Struct("<B")


class HostDataReadAck(EIEIOCommandMessage):
    """ Packet sent by the host computer to the SpiNNaker system in the\
        context of the buffering output technique to signal that the host has\
        received a request to read data
    """
    __slots__ = [
        "_sequence_no"]

    def __init__(self, sequence_no):
        super(HostDataReadAck, self).__init__(EIEIOCommandHeader(
            EIEIO_COMMAND_IDS.HOST_DATA_READ_ACK))
        self._sequence_no = sequence_no

    @property
    def sequence_no(self):
        return self._sequence_no

    @staticmethod
    def from_bytestring(command_header, data, offset):  # @UnusedVariable
        sequence_no = _PATTERN_B.unpack_from(data, offset)[0]

        return HostDataReadAck(sequence_no)

    @property
    def bytestring(self):
        byte_string = super(HostDataReadAck, self).bytestring
        byte_string += _PATTERN_B.pack(self.sequence_no)
        return byte_string
