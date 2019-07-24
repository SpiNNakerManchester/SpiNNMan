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

from spinnman.messages.scp.impl import SDRAMAlloc
from .abstract_multi_connection_process import AbstractMultiConnectionProcess


class MallocSDRAMProcess(AbstractMultiConnectionProcess):
    """ A process for allocating a block of SDRAM on a SpiNNaker chip.
    """
    __slots__ = [
        "_base_address"]

    def __init__(self, connection_selector):
        super(MallocSDRAMProcess, self).__init__(connection_selector)
        self._base_address = None

    def _handle_sdram_alloc_response(self, response):
        self._base_address = response.base_address

    def malloc_sdram(self, x, y, size, app_id, tag):
        """ Allocate space in the SDRAM space.
        """
        # pylint: disable=too-many-arguments
        self._send_request(SDRAMAlloc(x, y, app_id, size, tag),
                           self._handle_sdram_alloc_response)
        self._finish()
        self.check_for_error()

    @property
    def base_address(self):
        return self._base_address
