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
        super(GetHeapProcess, self).__init__(connection_selector)

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
