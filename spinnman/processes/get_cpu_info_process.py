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
from spinn_machine import CoreSubsets
from spinnman.model import CPUInfo, CPUInfos
from spinnman.constants import CPU_INFO_BYTES
from spinnman.utilities.utility_functions import get_vcpu_address
from spinnman.messages.scp.impl.read_memory import ReadMemory, Response
from .abstract_multi_connection_process import AbstractMultiConnectionProcess
from .abstract_multi_connection_process_connection_selector import (
    ConnectionSelector)

_INFO_PATTERN = struct.Struct("< 32s 3I 2B 2B 2I 2B H 3I 16s 2I 16x 4I")


class GetCPUInfoProcess(AbstractMultiConnectionProcess[Response]):
    __slots__ = ("_cpu_infos", )

    def __init__(self, connection_selector: ConnectionSelector):
        """
        :param ConnectionSelector connection_selector:
        """
        super().__init__(connection_selector)
        self._cpu_infos = CPUInfos()

    def _filter_and_add_repsonse(
            self, x: int, y: int, p: int, cpu_data: bytes):
        self._cpu_infos.add_info(CPUInfo(x, y, p, cpu_data))

    def __handle_response(self, x: int, y: int, p: int, response: Response):
        cpu_data = _INFO_PATTERN.unpack_from(response.data, response.offset)
        self._filter_and_add_repsonse(x, y, p, cpu_data)

    def get_cpu_info(self, core_subsets: CoreSubsets) -> CPUInfos:
        """
        :param ~spinn_machine.CoreSubsets core_subsets:
        :rtype: CPUInfos
        """
        with self._collect_responses():
            for core_subset in core_subsets:
                x, y = core_subset.x, core_subset.y
                for p in core_subset.processor_ids:
                    self._send_request(
                        ReadMemory(x, y, get_vcpu_address(p), CPU_INFO_BYTES),
                        functools.partial(self.__handle_response, x, y, p))

        return self._cpu_infos
