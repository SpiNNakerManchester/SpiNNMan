# Copyright (c) 2016 The University of Manchester
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
import functools
from spinnman.processes import AbstractMultiConnectionProcess
from spinnman.constants import SYSTEM_VARIABLE_BASE_ADDRESS
from spinnman.model import HeapElement
from spinnman.messages.spinnaker_boot import SystemVariableDefinition
from spinnman.messages.scp.impl import ReadMemory


HEAP_ADDRESS = SystemVariableDefinition.sdram_heap_address
_ADDRESS = struct.Struct("<I")
_HEAP_POINTER = struct.Struct("<4xI")
_ELEMENT_HEADER = struct.Struct("<II")


class GetHeapProcess(AbstractMultiConnectionProcess):
    __slots__ = [
        "_blocks",
        "_heap_address",
        "_next_block_address"]

    def __init__(self, connection_selector):
        """
        :param connection_selector:
        :type connection_selector:
            AbstractMultiConnectionProcessConnectionSelector
        """
        super().__init__(connection_selector)

        self._heap_address = None
        self._next_block_address = None
        self._blocks = list()

    def _read_heap_address_response(self, response):
        self._heap_address = _ADDRESS.unpack_from(
            response.data, response.offset)[0]

    def _read_heap_pointer(self, response):
        self._next_block_address = _HEAP_POINTER.unpack_from(
            response.data, response.offset)[0]

    def _read_next_block(self, block_address, response):
        self._next_block_address, free = _ELEMENT_HEADER.unpack_from(
            response.data, response.offset)
        if self._next_block_address != 0:
            self._blocks.append(HeapElement(
                block_address, self._next_block_address, free))

    def _read_address(self, chip_address, address, size, callback):
        (x, y) = chip_address
        self._send_request(
            ReadMemory(x, y, address, size), callback)
        self._finish()
        self.check_for_error()

    def get_heap(self, chip_address, pointer=HEAP_ADDRESS):
        """
        :param tuple(int,int) chip_address: x, y
        :param SystemVariableDefinition pointer:
        :rtype: list(HeapElement)
        """
        self._read_address(
            chip_address, SYSTEM_VARIABLE_BASE_ADDRESS + pointer.offset,
            pointer.data_type.value, self._read_heap_address_response)

        self._read_address(
            chip_address, self._heap_address, 8, self._read_heap_pointer)

        while self._next_block_address != 0:
            self._read_address(
                chip_address, self._next_block_address, 8,
                functools.partial(
                    self._read_next_block, self._next_block_address))

        return self._blocks
