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

from spinnman.messages.scp.impl.sdram_alloc import SDRAMAlloc, _AllocResponse
from .abstract_multi_connection_process import AbstractMultiConnectionProcess
from .abstract_multi_connection_process_connection_selector import (
    ConnectionSelector)


class MallocSDRAMProcess(AbstractMultiConnectionProcess[_AllocResponse]):
    """
    A process for allocating a block of SDRAM on a SpiNNaker chip.
    """
    __slots__ = ("_base_address", )

    def __init__(self, connection_selector: ConnectionSelector):
        """
        :param ConnectionSelector connection_selector:
        """
        super().__init__(connection_selector)
        self._base_address = 0

    def __handle_sdram_alloc_response(self, response: _AllocResponse):
        self._base_address = response.base_address

    def malloc_sdram(self, x: int, y: int, size: int, app_id: int, tag: int):
        """
        Allocate space in the SDRAM space.

        :param int x:
        :param int y:
        :param int size:
        :param int app_id:
        :param int tag:
        """
        # pylint: disable=too-many-arguments
        with self._collect_responses():
            self._send_request(SDRAMAlloc(x, y, app_id, size, tag),
                               self.__handle_sdram_alloc_response)

    @property
    def base_address(self) -> int:
        """
        The address of the allocated memory block.

        :rtype: int
        """
        return self._base_address
