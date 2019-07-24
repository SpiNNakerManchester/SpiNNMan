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

import os
import math
import time
import array
from six import iteritems
from .system_variable_boot_values import (
    SystemVariableBootValues, spinnaker_boot_values, SystemVariableDefinition)
from .spinnaker_boot_message import SpinnakerBootMessage
from .spinnaker_boot_op_code import SpinnakerBootOpCode
from spinnman.exceptions import (
    SpinnmanInvalidParameterException, SpinnmanIOException)

_BOOT_MESSAGE_DATA_WORDS = 256
_BOOT_MESSAGE_DATA_BYTES = _BOOT_MESSAGE_DATA_WORDS * 4
_BOOT_IMAGE_MAX_BYTES = 32 * 1024
_BOOT_DATA_FILE_NAME = "scamp.boot"
_BOOT_STRUCT_REPLACE_OFFSET = 384 // 4
_BOOT_STRUCT_REPLACE_LENGTH = 128 // 4
_BOOT_DATA_OPERAND_1 = ((_BOOT_MESSAGE_DATA_BYTES // 4) - 1) << 8


class SpinnakerBootMessages(object):
    """ Represents a set of boot messages to be sent to boot the board
    """
    __slots__ = [
        "_boot_data",
        "_n_bytes_to_read",
        "_no_data_packets"]

    def __init__(self, board_version=None, extra_boot_values=None):
        """ Builds the boot messages needed to boot the SpiNNaker machine

        :param board_version: The version of the board to be booted
        :type board_version: int
        :param extra_boot_values: Any additional values to be set during boot
        :type extra_boot_values: dict of SystemVariableDefinition to value
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: \
            If the board version is not supported
        :raise spinnman.exceptions.SpinnmanIOException: \
            If there is an error assembling the packets
        """
        if (board_version is not None and
                board_version not in spinnaker_boot_values):
            raise SpinnmanInvalidParameterException(
                "board_version", str(board_version), "Unknown board version")

        # Get the boot packet values
        if board_version is not None:
            spinnaker_boot_value = spinnaker_boot_values[board_version]
        else:
            spinnaker_boot_value = SystemVariableBootValues()

        current_time = int(time.time())
        spinnaker_boot_value.set_value(
            SystemVariableDefinition.unix_timestamp, current_time)
        spinnaker_boot_value.set_value(
            SystemVariableDefinition.boot_signature, current_time)
        spinnaker_boot_value.set_value(
            SystemVariableDefinition.is_root_chip, 1)

        # Set any additional values
        if extra_boot_values is not None:
            for variable, value in iteritems(extra_boot_values):
                spinnaker_boot_value.set_value(variable, value)

        # Get the data as an array, to be used later
        spinnaker_boot_data = array.array("I", spinnaker_boot_value.bytestring)

        # Find the data file and size
        boot_data_file, boot_data_size = self._get_boot_image_file()

        # Compute how many packets to send
        n_words_to_read = boot_data_size // 4
        self._no_data_packets = int(math.ceil(
            float(boot_data_size) / _BOOT_MESSAGE_DATA_BYTES))

        # Read the data
        boot_data = array.array("I")
        with open(boot_data_file, "rb") as f:
            boot_data.fromfile(f, n_words_to_read)

        # Replace the appropriate part with the custom boot options
        offset = _BOOT_STRUCT_REPLACE_OFFSET
        length = _BOOT_STRUCT_REPLACE_LENGTH
        boot_data[offset:offset + length] = spinnaker_boot_data[0:length]

        # Byte swap and store the data for later use
        boot_data.byteswap()
        self._boot_data = boot_data.tostring()
        self._n_bytes_to_read = n_words_to_read * 4

    @staticmethod
    def _get_boot_image_file():
        this_dir, _ = os.path.split(__file__)
        file_name = os.path.join(this_dir, "boot_data", _BOOT_DATA_FILE_NAME)
        file_size = os.stat(file_name).st_size
        if file_size > _BOOT_IMAGE_MAX_BYTES:
            raise SpinnmanIOException(
                "The boot file is too big at {} bytes (only files up to 32KB "
                "are acceptable".format(file_size))
        elif file_size % 4 != 0:
            raise SpinnmanIOException(
                "The boot file size of {} bytes must be divisible by 4".format(
                    file_size))
        return file_name, file_size

    def _get_packet_data(self, block_id):
        """ Read a packet of data
        """
        offset = block_id * _BOOT_MESSAGE_DATA_BYTES
        n_bytes = min(self._n_bytes_to_read - offset, _BOOT_MESSAGE_DATA_BYTES)
        return self._boot_data[offset:offset + n_bytes]

    @property
    def messages(self):
        """ Get an iterable of message to be sent.
        """

        # Construct and yield the start packet
        yield SpinnakerBootMessage(
            opcode=SpinnakerBootOpCode.FLOOD_FILL_START,
            operand_1=0, operand_2=0, operand_3=self._no_data_packets - 1)

        # Construct and yield the data packets
        for block_id in range(0, self._no_data_packets):
            operand_1 = _BOOT_DATA_OPERAND_1 | (block_id & 0xFF)
            yield SpinnakerBootMessage(
                opcode=SpinnakerBootOpCode.FLOOD_FILL_BLOCK,
                operand_1=operand_1, operand_2=0, operand_3=0,
                data=self._get_packet_data(block_id))

        # Construct and yield the end packet
        yield SpinnakerBootMessage(
            opcode=SpinnakerBootOpCode.FLOOD_FILL_CONTROL,
            operand_1=1, operand_2=0, operand_3=0)
