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

import os
import math
import time
import array
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
    """
    A set of boot messages to be sent to boot the board.
    """
    __slots__ = [
        "_boot_data",
        "_n_bytes_to_read",
        "_no_data_packets"]

    def __init__(self, board_version=None, extra_boot_values=None):
        """
        :param int board_version: The version of the board to be booted
        :param extra_boot_values: Any additional values to be set during boot
        :type extra_boot_values: dict(SystemVariableDefinition, object)
        :raise SpinnmanInvalidParameterException:
            If the board version is not supported
        :raise SpinnmanIOException:
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
            for variable, value in extra_boot_values.items():
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
        self._boot_data = boot_data.tobytes()
        self._n_bytes_to_read = n_words_to_read * 4

    @staticmethod
    def _get_boot_image_file():
        """
        :rtype: tuple(str,int)
        """
        this_dir, _ = os.path.split(__file__)
        file_name = os.path.join(this_dir, "boot_data", _BOOT_DATA_FILE_NAME)
        file_size = os.stat(file_name).st_size
        if file_size > _BOOT_IMAGE_MAX_BYTES:
            raise SpinnmanIOException(
                f"The boot file is too big at {file_size} bytes "
                "(only files up to 32KB are acceptable")
        elif file_size % 4 != 0:
            raise SpinnmanIOException(
                f"The boot file size of {file_size} bytes "
                "must be divisible by 4")
        return file_name, file_size

    def _get_packet_data(self, block_id):
        """
        Read a packet of data.

        :param int block_id:
        :rtype: bytes
        """
        offset = block_id * _BOOT_MESSAGE_DATA_BYTES
        n_bytes = min(self._n_bytes_to_read - offset, _BOOT_MESSAGE_DATA_BYTES)
        return self._boot_data[offset:offset + n_bytes]

    @property
    def messages(self):
        """
        An iterable of message to be sent.

        :rtype: iterable(SpinnakerBootMessage)
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
