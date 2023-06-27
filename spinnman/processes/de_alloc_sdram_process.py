
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
from typing import Optional
from spinnman.messages.scp.impl.sdram_de_alloc import (
    SDRAMDeAlloc, _SCPSDRAMDeAllocResponse)
from .abstract_multi_connection_process import AbstractMultiConnectionProcess
from .abstract_multi_connection_process_connection_selector import (
    ConnectionSelector)


class DeAllocSDRAMProcess(
        AbstractMultiConnectionProcess[_SCPSDRAMDeAllocResponse]):
    """
    .. warning::
        This class is currently deprecated and untested as there is no
        known use except for Transceiver.free_sdram and free_sdram_by_app_id
        which are both themselves deprecated.
    """
    __slots__ = ("_no_blocks_freed", )

    def __init__(self, connection_selector: ConnectionSelector):
        """
        :param ConnectionSelector connection_selector:
        """
        super().__init__(connection_selector)
        self._no_blocks_freed: Optional[int] = None

    def de_alloc_sdram(
            self, x: int, y: int, app_id: int,
            base_address: Optional[int] = None):
        """
        :param int x:
        :param int y:
        :param int app_id:
        :param base_address:
        :type base_address: int or None
        """
        # deallocate space in the SDRAM
        with self._collect_responses():
            self._send_request(
                SDRAMDeAlloc(x, y, app_id=app_id, base_address=base_address),
                callback=(self._handle_sdram_alloc_response
                          if base_address is None else None))

    def _handle_sdram_alloc_response(self, response: _SCPSDRAMDeAllocResponse):
        self._no_blocks_freed = response.number_of_blocks_freed

    @property
    def no_blocks_freed(self) -> int:
        """
        The number of blocks freed. Only valid if no base address was supplied
        in the request.
        """
        assert self._no_blocks_freed is not None, "wrong request type"
        return self._no_blocks_freed
