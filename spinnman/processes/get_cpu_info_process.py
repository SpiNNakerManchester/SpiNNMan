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
import struct
from spinnman.model import CPUInfo, CPUInfos
from spinnman.constants import CPU_INFO_BYTES
from spinnman.utilities.utility_functions import get_vcpu_address
from spinnman.messages.scp.impl import ReadMemory
from .abstract_multi_connection_process import AbstractMultiConnectionProcess

_INFO_PATTERN = struct.Struct("< 32s 3I 2B 2B 2I 2B H 3I 16s 2I 16x 4I")


class GetCPUInfoProcess(AbstractMultiConnectionProcess):
    __slots__ = [
        "_cpu_infos"]

    def __init__(self, connection_selector):
        """
        :param connection_selector:
        :type connection_selector:
            AbstractMultiConnectionProcessConnectionSelector
        """
        super().__init__(connection_selector)
        self._cpu_infos = CPUInfos()

    def _filter_and_add_repsonse(self, x, y, p, cpu_data):
        self._cpu_infos.add_info(CPUInfo(x, y, p, cpu_data))

    def __handle_response(self, x, y, p, response):
        cpu_data = _INFO_PATTERN.unpack_from(response.data, response.offset)
        self._filter_and_add_repsonse(x, y, p, cpu_data)

    def get_cpu_info(self, core_subsets):
        """
        :param ~spinn_machine.CoreSubsets core_subsets:
        :rtype: list(CPUInfo)
        """
        for core_subset in core_subsets:
            x = core_subset.x
            y = core_subset.y

            for p in core_subset.processor_ids:
                self._send_request(
                    ReadMemory(x, y, get_vcpu_address(p), CPU_INFO_BYTES),
                    functools.partial(self.__handle_response, x, y, p))
        self._finish()
        self.check_for_error()

        return self._cpu_infos
