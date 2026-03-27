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
from spinn_utilities.overrides import overrides
from spinnman.constants import EIEIO_COMMAND_IDS
from .eieio_command_message import EIEIOCommandMessage
from .eieio_command_header import EIEIOCommandHeader

_PATTERN_B = struct.Struct("<B")


class HostDataReadAck(EIEIOCommandMessage):
    """
    Packet sent by the host computer to the SpiNNaker system in the
    context of the buffering output technique to signal that the host has
    received a request to read data.
    """
    __slots__ = "_sequence_no",

    def __init__(self, sequence_no: int):
        """

        :param sequence_no:
        """
        super().__init__(
            EIEIOCommandHeader(EIEIO_COMMAND_IDS.HOST_DATA_READ_ACK))
        self._sequence_no = sequence_no

    @property
    def sequence_no(self) -> int:
        """ Gets the sequence_no passed into the init. """
        return self._sequence_no

    @staticmethod
    @overrides(EIEIOCommandMessage.from_bytestring)
    def from_bytestring(command_header: EIEIOCommandHeader, data: bytes,
                        offset: int) -> "HostDataReadAck":
        sequence_no = _PATTERN_B.unpack_from(data, offset)[0]

        return HostDataReadAck(sequence_no)

    @property
    @overrides(EIEIOCommandMessage.bytestring)
    def bytestring(self) -> bytes:
        byte_string = super().bytestring
        byte_string += _PATTERN_B.pack(self.sequence_no)
        return byte_string
