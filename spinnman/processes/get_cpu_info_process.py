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
from typing import List, Sequence
from spinn_machine import CoreSubsets
from spinnman.model import CPUInfo
from spinnman.constants import CPU_INFO_BYTES
from spinnman.utilities.utility_functions import get_vcpu_address
from spinnman.messages.scp.impl.read_memory import ReadMemory, Response
from .abstract_multi_connection_process import AbstractMultiConnectionProcess
from .abstract_multi_connection_process_connection_selector import (
    AbstractMultiConnectionProcessConnectionSelector)


class GetCPUInfoProcess(AbstractMultiConnectionProcess[Response]):
    __slots__ = ("_cpu_info", )

    def __init__(self, connection_selector:
                 AbstractMultiConnectionProcessConnectionSelector):
        """
        :param connection_selector:
        :type connection_selector:
            AbstractMultiConnectionProcessConnectionSelector
        """
        super().__init__(connection_selector)
        self._cpu_info: List[CPUInfo] = list()

    def __handle_response(self, x: int, y: int, p: int, response: Response):
        self._cpu_info.append(CPUInfo(x, y, p, response.data, response.offset))

    def get_cpu_info(self, core_subsets: CoreSubsets) -> Sequence[CPUInfo]:
        """
        :param ~spinn_machine.CoreSubsets core_subsets:
        :rtype: list(CPUInfo)
        """
        with self._collect_responses():
            for core_subset in core_subsets:
                x, y = core_subset.x, core_subset.y
                for p in core_subset.processor_ids:
                    self._send_request(
                        ReadMemory(x, y, get_vcpu_address(p), CPU_INFO_BYTES),
                        functools.partial(self.__handle_response, x, y, p))

        return self._cpu_info
