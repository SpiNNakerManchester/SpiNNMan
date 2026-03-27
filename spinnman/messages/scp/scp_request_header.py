# Copyright (c) 2014 The University of Manchester
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

from enum import Enum
import struct
from typing import Union
from typing_extensions import TypeAlias
from spinnman.messages.scp.enums import SCPCommand

_TWO_SHORTS = struct.Struct("<2H")
_Command: TypeAlias = Union[SCPCommand, Enum]


class SCPRequestHeader(object):
    """
    Represents the header of an SCP Request.
    """
    __slots__ = (
        "_command",
        "_sequence")

    def __init__(self, command: _Command, sequence: int = 0):
        """
        :param command: The SCP command
        :param sequence:
            The number of the SCP packet in order of all packets
            sent or received, between 0 and 65535
        """
        self._command = command
        self._sequence = sequence

    @property
    def command(self) -> _Command:
        """ The command of the SCP packet. """
        return self._command

    @property
    def sequence(self) -> int:
        """ The sequence number of the SCP packet, between 0 and 65535. """
        return self._sequence

    @sequence.setter
    def sequence(self, sequence: int) -> None:
        """
        Set the sequence number of the SCP packet.

        :param sequence: The sequence number to set, between 0 and 65535
        """
        self._sequence = sequence

    @property
    def bytestring(self) -> bytes:
        """ The header as a byte-string. """
        return _TWO_SHORTS.pack(self._command.value, self._sequence)
