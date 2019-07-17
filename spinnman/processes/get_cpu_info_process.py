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

import functools
from spinnman.model import CPUInfo
from spinnman.constants import CPU_INFO_BYTES
from spinnman.utilities.utility_functions import get_vcpu_address
from spinnman.messages.scp.impl import ReadMemory
from .abstract_multi_connection_process import AbstractMultiConnectionProcess


class GetCPUInfoProcess(AbstractMultiConnectionProcess):
    __slots__ = [
        "_cpu_info"]

    def __init__(self, connection_selector):
        super(GetCPUInfoProcess, self).__init__(connection_selector)
        self._cpu_info = list()

    def handle_response(self, x, y, p, response):
        self._cpu_info.append(CPUInfo(x, y, p, response.data, response.offset))

    def get_cpu_info(self, core_subsets):
        for core_subset in core_subsets:
            x = core_subset.x
            y = core_subset.y

            for p in core_subset.processor_ids:
                self._send_request(
                    ReadMemory(x, y, get_vcpu_address(p), CPU_INFO_BYTES),
                    functools.partial(self.handle_response, x, y, p))
        self._finish()
        self.check_for_error()

        return self._cpu_info
