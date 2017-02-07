"""
SpinnakerBootMessages
"""

# spinnman imports
from spinnman.messages.spinnaker_boot._system_variables import \
    _system_variable_boot_values as variable_boot_values
from spinnman.messages.spinnaker_boot._system_variables.\
    _system_variable_boot_values import \
    SystemVariableDefinition
from spinnman.messages.spinnaker_boot._system_variables\
    ._system_variable_boot_values import SystemVariableBootValues
from spinnman.messages.spinnaker_boot.spinnaker_boot_message \
    import SpinnakerBootMessage
from spinnman.messages.spinnaker_boot.spinnaker_boot_op_code \
    import SpinnakerBootOpCode

from spinnman.exceptions import SpinnmanInvalidParameterException
from spinnman.exceptions import SpinnmanIOException

# general imports
import os
import math
import time
import array

_BOOT_MESSAGE_DATA_WORDS = 256
_BOOT_MESSAGE_DATA_BYTES = _BOOT_MESSAGE_DATA_WORDS * 4
_BOOT_IMAGE_MAX_BYTES = 32 * 1024
_BOOT_DATA_FILE_NAME = "scamp.boot"
_BOOT_STRUCT_REPLACE_OFFSET = 384 / 4
_BOOT_STRUCT_REPLACE_LENGTH = 128 / 4
_BOOT_DATA_OPERAND_1 = ((_BOOT_MESSAGE_DATA_BYTES / 4) - 1) << 8


class SpinnakerBootMessages(object):
    """ Represents a set of boot messages to be sent to boot the board
    """

    def __init__(self, board_version=None):
        """
        builds the boot messages needed to boot the spinnaker machine

        :param board_version: The version of the board to be booted
        :type board_version: int
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If the\
                    board version is not supported
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    assembling the packets
        """
        if (board_version is not None and
                board_version not in
                variable_boot_values.spinnaker_boot_values):
            raise SpinnmanInvalidParameterException(
                "board_version", str(board_version), "Unknown board version")

        # Get the boot packet values
        if board_version is not None:
            spinnaker_boot_value = variable_boot_values.spinnaker_boot_values[
                board_version]
        else:
            spinnaker_boot_value = SystemVariableBootValues()

        current_time = int(time.time())
        spinnaker_boot_value.set_value(
            SystemVariableDefinition.unix_timestamp, current_time)
        spinnaker_boot_value.set_value(
            SystemVariableDefinition.boot_signature, current_time)
        spinnaker_boot_value.set_value(
            SystemVariableDefinition.is_root_chip, 1)

        # Get the data as an array, to be used later
        self._spinnaker_boot_data = array.array(
            "I", spinnaker_boot_value.bytestring)

        # Find the data file and size
        this_dir, _ = os.path.split(__file__)
        boot_data_file_name = os.path.join(
            this_dir, "boot_data", _BOOT_DATA_FILE_NAME)
        boot_data_file_size = os.stat(boot_data_file_name).st_size
        if boot_data_file_size > _BOOT_IMAGE_MAX_BYTES:
            raise SpinnmanIOException(
                "The boot file is too big at {} bytes ("
                "only files up to 32KB are acceptable".format(
                    boot_data_file_size))
        elif boot_data_file_size % 4 != 0:
            raise SpinnmanIOException(
                "The boot file size of {} bytes must"
                " be divisible by 4".format(boot_data_file_size))

        # Compute how many packets to send
        self._boot_data_file = open(boot_data_file_name, "rb")
        self._no_data_packets = int(math.ceil(
            float(boot_data_file_size) / float(_BOOT_MESSAGE_DATA_BYTES)))
        self._n_words_to_read = boot_data_file_size / 4

    def _get_packet_data(self, replace_data=None, offset=None, length=None):

        # Read the next bit of data
        data = array.array("I")
        n_words = min((self._n_words_to_read, _BOOT_MESSAGE_DATA_WORDS))
        self._n_words_to_read -= n_words
        data.fromfile(self._boot_data_file, n_words)

        # If there is any replace_data, replace it now
        if replace_data is not None:
            data[offset:offset + length] = replace_data[0:length]

        # Byte-swap the data to make it big-endian and return
        data.byteswap()
        return data.tostring()

    @property
    def messages(self):
        """ Get an iterable of message to be sent.
        """

        # Construct and yield the start packet
        yield SpinnakerBootMessage(
            opcode=SpinnakerBootOpCode.FLOOD_FILL_START,
            operand_1=0, operand_2=0, operand_3=self._no_data_packets - 1)

        # Construct and yield the first data packet replacing the appropriate
        # part with the boot data values
        yield SpinnakerBootMessage(
            opcode=SpinnakerBootOpCode.FLOOD_FILL_BLOCK,
            operand_1=_BOOT_DATA_OPERAND_1 | 0, operand_2=0, operand_3=0,
            data=self._get_packet_data(
                self._spinnaker_boot_data, _BOOT_STRUCT_REPLACE_OFFSET,
                _BOOT_STRUCT_REPLACE_LENGTH))

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
