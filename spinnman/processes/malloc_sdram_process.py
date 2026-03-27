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

import functools
from typing import List, Tuple
from spinnman.messages.scp.impl.sdram_alloc import SDRAMAlloc, _AllocResponse
from .abstract_multi_connection_process import AbstractMultiConnectionProcess
from .abstract_multi_connection_process_connection_selector import (
    ConnectionSelector)


class MallocSDRAMProcess(AbstractMultiConnectionProcess[_AllocResponse]):
    """
    A process for allocating a block of SDRAM on a SpiNNaker chip.
    """
    __slots__ = ["__base_addresses",]

    def __init__(self, connection_selector: ConnectionSelector):
        """
        :param connection_selector:
        """
        super().__init__(connection_selector)
        self.__base_addresses: List[int] = []

    def __handle_sdram_alloc_response(
            self, pos: int, response: _AllocResponse) -> None:
        self.__base_addresses[pos] = response.base_address

    def malloc_sdram(
            self, x: int, y: int, size: int, app_id: int, tag: int) -> None:
        """
        Allocate space in the SDRAM space.

        :param x:
        :param y:
        :param size:
        :param app_id:
        :param tag:
        """
        self.__base_addresses = [0]
        with self._collect_responses():
            self._send_request(
                SDRAMAlloc(x, y, app_id, size, tag),
                functools.partial(self.__handle_sdram_alloc_response, 0))

    def malloc_sdram_multi(
            self, allocations: List[Tuple[int, int, int, int, int]]) -> None:
        """
        Allocate space in the SDRAM space for multiple chips

        :param allocations:
            List of (x, y, size, app_id, tag)
        """
        self.__base_addresses = [0] * len(allocations)
        with self._collect_responses():
            for i, (x, y, size, app_id, tag) in enumerate(allocations):
                self._send_request(
                    SDRAMAlloc(x, y, app_id, size, tag),
                    functools.partial(
                        self.__handle_sdram_alloc_response, i))

    @property
    def base_address(self) -> int:
        """
        The address of the allocated memory block.
        """
        return self.__base_addresses[0]

    @property
    def base_addresses(self) -> List[int]:
        """
        The addresses of the allocated memory blocks.
        """
        return self.__base_addresses
