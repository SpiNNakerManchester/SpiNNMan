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

import struct
from spinnman.exceptions import SpinnmanInvalidParameterException
from .spinnaker_boot_op_code import SpinnakerBootOpCode

_PATTERN_HIIII = struct.Struct(">HIIII")
_PATTERN_2xIIII = struct.Struct("2xIIII")
BOOT_MESSAGE_VERSION = 1


class SpinnakerBootMessage(object):
    """
    A message used for booting the board.
    """
    __slots__ = [
        "_data",
        "_offset",
        "_opcode",
        "_operand_1",
        "_operand_2",
        "_operand_3"]

    def __init__(self, opcode, operand_1, operand_2, operand_3, data=None,
                 offset=0):
        """
        :param SpinnakerBootOpCode opcode: The operation of this packet
        :param int operand_1: The first operand
        :param int operand_2: The second operand
        :param int operand_3: The third operand
        :param data: The optional data, up to 256 words
        :type data: bytes or bytearray
        :param int offset: The offset of the valid data
        :raise SpinnmanInvalidParameterException:
            If the opcode is not a valid value
        """
        # pylint: disable=too-many-arguments
        if data is not None and len(data) > (256 * 4):
            raise SpinnmanInvalidParameterException(
                "len(data)", str(len(data)),
                "A boot packet can contain at most 256 words of data")

        self._opcode = opcode
        self._operand_1 = operand_1
        self._operand_2 = operand_2
        self._operand_3 = operand_3
        self._data = data
        self._offset = offset

    @property
    def opcode(self):
        """
        The operation of this packet.

        :rtype: SpinnakerBootOpCode
        """
        return self._opcode

    @property
    def operand_1(self):
        """
        The first operand.

        :rtype: int
        """
        return self._operand_1

    @property
    def operand_2(self):
        """
        The second operand.

        :rtype: int
        """
        return self._operand_2

    @property
    def operand_3(self):
        """
        The third operand.

        :rtype: int
        """
        return self._operand_3

    @property
    def data(self):
        """
        The data, or `None` if no data.

        :rtype: bytes or bytearray
        """
        return self._data

    @property
    def bytestring(self):
        """
        The message as a byte-string.

        :rtype: bytes
        """
        data = b""
        if self._data is not None:
            data = self._data[self._offset:]
        return _PATTERN_HIIII.pack(
            BOOT_MESSAGE_VERSION, self._opcode.value,
            self._operand_1, self._operand_2, self._operand_3) + data

    @staticmethod
    def from_bytestring(data, offset):
        """
        :param bytes data:
        :param int offset:
        :rtype: SpinnakerBootMessage
        """
        (opcode_value, operand_1, operand_2, operand_3) = \
            _PATTERN_2xIIII.unpack_from(data, offset)
        the_data = None
        if len(data) - offset > 0:
            the_data = data
        return SpinnakerBootMessage(
            SpinnakerBootOpCode(opcode_value), operand_1, operand_2, operand_3,
            the_data, offset + 18)
