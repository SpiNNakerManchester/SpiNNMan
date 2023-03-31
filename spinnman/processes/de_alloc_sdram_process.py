
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

from spinnman.messages.scp.impl import SDRAMDeAlloc
from .abstract_multi_connection_process import AbstractMultiConnectionProcess


class DeAllocSDRAMProcess(AbstractMultiConnectionProcess):
    """
    .. warning::
        This class is currently deprecated and untested as there is no
        known use except for Transceiver.free_sdram and free_sdram_by_app_id
        which are both themselves deprecated.
    """
    __slots__ = [
        "_no_blocks_freed"]

    def __init__(self, connection_selector):
        """
        :param connection_selector:
        :type connection_selector:
            AbstractMultiConnectionProcessConnectionSelector
        """
        super().__init__(connection_selector)
        self._no_blocks_freed = None

    def de_alloc_sdram(self, x, y, app_id, base_address=None):
        """
        :param int x:
        :param int y:
        :param int app_id:
        :param base_address:
        :type base_address: int or None
        """
        callback = None
        # deallocate space in the SDRAM
        if base_address is None:
            callback = self._handle_sdram_alloc_response
        self._send_request(SDRAMDeAlloc(x, y, app_id, base_address),
                           callback=callback)
        self._finish()
        self.check_for_error()

    def _handle_sdram_alloc_response(self, response):
        self._no_blocks_freed = response.number_of_blocks_freed

    @property
    def no_blocks_freed(self):
        """
        :rtype: int
        """
        return self._no_blocks_freed
