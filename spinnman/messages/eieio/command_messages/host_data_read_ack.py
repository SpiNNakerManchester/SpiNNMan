# Copyright (c) 2017 The University of Manchester
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
from .eieio_command_message import EIEIOCommandMessage
from .eieio_command_header import EIEIOCommandHeader
from spinnman.constants import EIEIO_COMMAND_IDS

_PATTERN_B = struct.Struct("<B")


class HostDataReadAck(EIEIOCommandMessage):
    """
    Packet sent by the host computer to the SpiNNaker system in the
    context of the buffering output technique to signal that the host has
    received a request to read data.
    """
    __slots__ = [
        "_sequence_no"]

    def __init__(self, sequence_no):
        super().__init__(
            EIEIOCommandHeader(EIEIO_COMMAND_IDS.HOST_DATA_READ_ACK))
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
        byte_string = super().bytestring
        byte_string += _PATTERN_B.pack(self.sequence_no)
        return byte_string
