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
from enum import Enum
from spinnman.exceptions import SpinnmanInvalidParameterException

_ONE_SHORT = struct.Struct("<H")


class EIEIOCommandHeader(object):
    """
    EIEIO header for command packets.
    """
    __slots__ = [
        "_command"]

    def __init__(self, command):
        if isinstance(command, Enum):
            command = command.value
        if command < 0 or command >= 16384:
            raise SpinnmanInvalidParameterException(
                "command", command,
                "parameter command is outside the allowed range (0 to 16383)")
        self._command = command

    @property
    def command(self):
        return self._command

    @staticmethod
    def from_bytestring(data, offset):
        """
        Read an EIEIO command header from a byte-string.

        :param data: The byte-string to read the data from
        :type data: bytes or bytearray
        :param int offset: The offset where the valid data starts
        :return: an EIEIO command header
        :rtype: EIEIOCommandHeader
        :raise SpinnmanIOException:
            If there is an error reading from the reader
        :raise SpinnmanInvalidParameterException:
            If there is an error setting any of the values
        """
        command_header = _ONE_SHORT.unpack_from(data, offset)[0]
        command = command_header & 0x3FFF

        return EIEIOCommandHeader(command)

    @property
    def bytestring(self):
        """
        The byte-string of the header.

        :rtype: bytes
        """
        return _ONE_SHORT.pack(0 << 15 | 1 << 14 | self._command)
