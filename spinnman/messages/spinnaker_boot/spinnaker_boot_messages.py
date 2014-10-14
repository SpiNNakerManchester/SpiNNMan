from spinnman.messages.spinnaker_boot._system_variables._system_variable_boot_values import spinnaker_boot_values
from spinnman.messages.spinnaker_boot._system_variables._system_variable_boot_values import _SystemVariableDefinition
from spinnman.messages.spinnaker_boot.spinnaker_boot_message import SpinnakerBootMessage
from spinnman.messages.spinnaker_boot.spinnaker_boot_op_code import SpinnakerBootOpCode

from spinnman.exceptions import SpinnmanInvalidParameterException
from spinnman.exceptions import SpinnmanIOException

from spinnman.data.file_data_reader import FileDataReader
from spinnman.data.big_endian_byte_array_byte_writer import BigEndianByteArrayByteWriter
from spinnman.data.little_endian_byte_array_byte_writer import LittleEndianByteArrayByteWriter
from spinnman.data.little_endian_data_reader_byte_reader import LittleEndianDataReaderByteReader

from spinnman._utils import _get_int_from_little_endian_bytearray
from spinnman._utils import _put_int_in_big_endian_byte_array

import os
import math
import time

_BOOT_MESSAGE_DATA_BYTES = 1024
_BOOT_IMAGE_MAX_BYTES = 32 * 1024
_BOOT_DATA_FILE_NAME = "scamp-133.boot"
_BOOT_STRUCT_REPLACE_OFFSET = 0x180
_BOOT_STRUCT_REPLACE_LENGTH = 0x80
_BOOT_DATA_OPERAND_1 = ((_BOOT_MESSAGE_DATA_BYTES / 4) - 1) << 8


class SpinnakerBootMessages(object):
    """ Represents a set of boot messages to be sent to boot the board
    """

    def __init__(self, board_version):
        """

        :param board_version: The version of the board to be booted
        :type board_version: int
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If the\
                    board version is not supported
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    assembling the packets
        """
        if board_version not in spinnaker_boot_values:
            raise SpinnmanInvalidParameterException(
                    "board_version", board_version, "Unknown board version")

        # Get the boot packet values
        spinnaker_boot_value = spinnaker_boot_values[board_version]
        current_time = int(time.time())
        spinnaker_boot_value.set_value(
                _SystemVariableDefinition.unix_timestamp, current_time)
        spinnaker_boot_value.set_value(
                _SystemVariableDefinition.boot_signature, current_time)
        spinnaker_boot_value.set_value(
                _SystemVariableDefinition.is_root_chip, 1)
        boot_data_writer = LittleEndianByteArrayByteWriter()
        spinnaker_boot_value.write_values(boot_data_writer)
        self._spinnaker_boot_data = boot_data_writer.data

        # endian-swap the boot data word by word
        for offset in range(0, len(self._spinnaker_boot_data), 4):
            word = _get_int_from_little_endian_bytearray(
                    self._spinnaker_boot_data, offset)
            _put_int_in_big_endian_byte_array(
                    self._spinnaker_boot_data, offset, word)

        # Find the data file and size
        this_dir, _ = os.path.split(__file__)
        boot_data_file_name = os.path.join(this_dir, "boot_data",
                _BOOT_DATA_FILE_NAME)
        boot_data_file_status = os.stat(boot_data_file_name)
        boot_data_file_size = boot_data_file_status.st_size
        if boot_data_file_size > _BOOT_IMAGE_MAX_BYTES:
            raise SpinnmanIOException("The boot file is too big at {} bytes ("
                    "only files up to 32KB are acceptable".format(
                            boot_data_file_size))
        elif boot_data_file_size % 4 != 0:
            raise SpinnmanIOException("The boot file size of {} bytes must"
                    " be divisible by 4".format(boot_data_file_size))

        # Try to open the file
        self._boot_data_reader = FileDataReader(boot_data_file_name)
        self._boot_data_byte_reader = LittleEndianDataReaderByteReader(
                self._boot_data_reader)

        # Compute how many packets to send
        self._no_data_packets = int(math.ceil(float(boot_data_file_size)
                / float(_BOOT_MESSAGE_DATA_BYTES)))
        self._no_bytes_to_read = boot_data_file_size

    def _get_packet_data(self):
        writer = BigEndianByteArrayByteWriter()
        while (self._no_bytes_to_read > 0
                and writer.get_n_bytes_written() < _BOOT_MESSAGE_DATA_BYTES):
            writer.write_int(self._boot_data_byte_reader.read_int())
            self._no_bytes_to_read -= 4

        # Pad the packet
        while writer.get_n_bytes_written() < _BOOT_MESSAGE_DATA_BYTES:
            writer.write_int(0)
        return writer.data

    @property
    def messages(self):
        """ Get an iterable of message to be sent.
        """

        # Construct and yield the start packet
        yield SpinnakerBootMessage(
                opcode=SpinnakerBootOpCode.FLOOD_FILL_START,
                operand_1=0, operand_2=0, operand_3=self._no_data_packets - 1,
                data=[])

        # Construct and yield the first data packet replacing the appropriate
        # part with the boot data values
        data = self._get_packet_data()
        data[_BOOT_STRUCT_REPLACE_OFFSET:(_BOOT_STRUCT_REPLACE_OFFSET
                + _BOOT_STRUCT_REPLACE_LENGTH)] = self._spinnaker_boot_data[0:
                        _BOOT_STRUCT_REPLACE_LENGTH]
        operand_1 = _BOOT_DATA_OPERAND_1 | 0
        yield SpinnakerBootMessage(
                opcode=SpinnakerBootOpCode.FLOOD_FILL_BLOCK,
                operand_1=operand_1, operand_2=0, operand_3=0, data=data)

        # Construct an yield the remaining packets
        for block_id in range(1, self._no_data_packets):
            operand_1 = _BOOT_DATA_OPERAND_1 | (block_id & 0xFF)
            yield SpinnakerBootMessage(
                    opcode=SpinnakerBootOpCode.FLOOD_FILL_BLOCK,
                    operand_1=operand_1, operand_2=0, operand_3=0,
                    data=self._get_packet_data())

        # Construct and yield the end packet
        yield SpinnakerBootMessage(
                opcode=SpinnakerBootOpCode.FLOOD_FILL_CONTROL,
                operand_1=1, operand_2=0, operand_3=0)
