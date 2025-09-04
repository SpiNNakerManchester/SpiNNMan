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

import functools
import struct
from typing import Callable, List, Sequence
from spinn_utilities.typing.coords import XY, XYP
from spinnman.processes import AbstractMultiConnectionProcess
from spinnman.constants import SYSTEM_VARIABLE_BASE_ADDRESS
from spinnman.model import HeapElement
from spinnman.messages.spinnaker_boot import SystemVariableDefinition
from spinnman.messages.scp.impl.read_memory import ReadMemory, Response
from .abstract_multi_connection_process_connection_selector import (
    ConnectionSelector)


HEAP_ADDRESS = SystemVariableDefinition.sdram_heap_address
_ADDRESS = struct.Struct("<I")
_HEAP_POINTER = struct.Struct("<4xI")
_ELEMENT_HEADER = struct.Struct("<II")


class GetHeapProcess(AbstractMultiConnectionProcess[Response]):
    """
    Gets Heap information using the provided connector.

    """
    __slots__ = (
        "_blocks",
        "_heap_address",
        "_next_block_address")

    def __init__(self, connection_selector: ConnectionSelector):
        """
        :param connection_selector:
        """
        super().__init__(connection_selector)

        self._heap_address = 0
        self._next_block_address = 0
        self._blocks: List[HeapElement] = list()

    def _read_heap_address_response(self, response: Response) -> None:
        self._heap_address = _ADDRESS.unpack_from(
            response.data, response.offset)[0]

    def _read_heap_pointer(self, response: Response) -> None:
        self._next_block_address = _HEAP_POINTER.unpack_from(
            response.data, response.offset)[0]

    def _read_next_block(self, block_address: int, response: Response) -> None:
        self._next_block_address, free = _ELEMENT_HEADER.unpack_from(
            response.data, response.offset)
        if self._next_block_address != 0:
            self._blocks.append(HeapElement(
                block_address, self._next_block_address, free))

    def __read_address(
            self, core_coords: XYP, address: int, size: int,
            callback: Callable[[Response], None]) -> None:
        with self._collect_responses():
            self._send_request(
                ReadMemory(core_coords, address, size), callback)

    def get_heap(self, chip_coords: XY,
                 pointer: SystemVariableDefinition = HEAP_ADDRESS
                 ) -> Sequence[HeapElement]:
        """
        :param chip_coords: x, y
        :param pointer:
        :returns: List of HeapElements
        """
        x, y = chip_coords
        core_coords = (x, y, 0)
        self.__read_address(
            core_coords, SYSTEM_VARIABLE_BASE_ADDRESS + pointer.offset,
            pointer.data_type.value, self._read_heap_address_response)

        self.__read_address(
            core_coords, self._heap_address, 8, self._read_heap_pointer)

        while self._next_block_address != 0:
            self.__read_address(
                core_coords, self._next_block_address, 8,
                functools.partial(
                    self._read_next_block, self._next_block_address))

        return self._blocks
