from spinnman.exceptions import SpinnmanInvalidParameterException
from .spinnaker_boot_op_code import SpinnakerBootOpCode

import struct

BOOT_MESSAGE_VERSION = 1


class SpinnakerBootMessage(object):
    """ A message used for booting the board
    """

    def __init__(self, opcode, operand_1, operand_2, operand_3, data=None,
                 offset=0):
        """
        :param opcode: The operation of this packet
        :type opcode:\
                    :py:class:`spinnman.messages.spinnaker_boot.spinnaker_boot_op_code.SpinnakerBootOpCode`
        :param operand_1: The first operand
        :type operand_1: int
        :param operand_2: The second operand
        :type operand_2: int
        :param operand_3: The third operand
        :type operand_3: int
        :param data: The optional data, up to 256 words
        :type data: str
        :param offset: The offset of the valid data
        :type offset: int
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If the\
                    opcode is not a valid value
        """
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
        """ The operation of this packet

        :return: The operation code
        :rtype:\
                :py:class:`spinnman.messages.spinnaker_boot.spinnaker_boot_op_code.SpinnakerBootOpCode`
        """
        return self._opcode

    @property
    def operand_1(self):
        """ The first operand

        :return: The operand
        :rtype: int
        """
        return self._operand_1

    @property
    def operand_2(self):
        """ The second operand

        :return: The second operand
        :rtype: int
        """
        return self._operand_2

    @property
    def operand_3(self):
        """ The third operand

        :return: The third operand
        :rtype: int
        """
        return self._operand_3

    @property
    def data(self):
        """ The data

        :return: The data or None if no data
        :rtype: bytearray
        """
        return self._data

    @property
    def bytestring(self):
        """ The message as a bytestring
        """
        data = ""
        if self._data is not None:
            data = self._data[self._offset:]
        return struct.pack(
            ">HIIII", BOOT_MESSAGE_VERSION, self._opcode.value,
            self._operand_1, self._operand_2, self._operand_3) + data

    @staticmethod
    def from_bytestring(data, offset):
        (opcode_value, operand_1, operand_2, operand_3) = struct.unpack_from(
            "2xIIII", data, offset)
        the_data = None
        if len(data) - offset > 0:
            the_data = data
        return SpinnakerBootMessage(
            SpinnakerBootOpCode(opcode_value), operand_1, operand_2, operand_3,
            the_data, offset + 18)
