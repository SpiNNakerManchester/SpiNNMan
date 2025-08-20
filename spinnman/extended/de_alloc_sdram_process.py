
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
from spinnman.processes import AbstractMultiConnectionProcess
from spinnman.processes import ConnectionSelector


class DeAllocSDRAMProcess(AbstractMultiConnectionProcess):
    """
    .. warning::
        This class is currently deprecated and untested as there is no
        known use except for Transceiver.free_sdram and free_sdram_by_app_id
        which are both themselves deprecated.
    """
    __slots__ = ("_no_blocks_freed", )

    def __init__(self, connection_selector: ConnectionSelector) -> None:
        """
        :param connection_selector:
        """
        super().__init__(connection_selector)
        self._no_blocks_freed: Optional[int] = None

    def de_alloc_all_app_sdram(self, x: int, y: int, app_id: int) -> None:
        """
        Currently not used!

        :param x:
        :param y:
        :param app_id:
        """
        # deallocate space in the SDRAM
        with self._collect_responses():
            self._send_request(SDRAMDeAlloc(x, y, app_id=app_id),
                               callback=self.__handle_sdram_alloc_response)

    def de_alloc_sdram(self, x: int, y: int, base_address: int) -> None:
        """
        Currently not used!

        :param x:
        :param y:
        :param base_address:
        """
        with self._collect_responses():
            self._send_request(SDRAMDeAlloc(x, y, base_address=base_address),
                               callback=None)

    def __handle_sdram_alloc_response(
            self, response: _SCPSDRAMDeAllocResponse) -> None:
        self._no_blocks_freed = response.number_of_blocks_freed

    @property
    def no_blocks_freed(self) -> Optional[int]:
        """ number of blocks freed """
        return self._no_blocks_freed
