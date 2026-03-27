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
from typing import cast
from spinn_machine import CoreSubsets
from spinnman.model import CPUInfos
from spinnman.model.cpu_info import CPUInfo, VcpuT, _VCPU_PATTERN
from spinnman.constants import CPU_INFO_BYTES
from spinnman.utilities.utility_functions import get_vcpu_address
from spinnman.messages.scp.impl.read_memory import ReadMemory, Response
from .abstract_multi_connection_process import AbstractMultiConnectionProcess
from .abstract_multi_connection_process_connection_selector import (
    ConnectionSelector)


class GetCPUInfoProcess(AbstractMultiConnectionProcess[Response]):
    """
    Gets the CPU for processors over the provided connection.

    This base class returns info for all states.
    """
    __slots__ = ("__cpu_infos", )

    def __init__(self, connection_selector: ConnectionSelector):
        """
        :param connection_selector:
        """
        super().__init__(connection_selector)
        self.__cpu_infos = CPUInfos()

    def _is_desired(self, cpu_info: CPUInfo) -> bool:
        # cpu_info defined as used in subclasses
        _ = cpu_info
        return True

    def __handle_response(
            self, x: int, y: int, p: int, response: Response) -> None:
        cpu_data = cast(VcpuT, _VCPU_PATTERN.unpack_from(
            response.data, response.offset))
        cpu_info = CPUInfo(x, y, p, cpu_data)
        if self._is_desired(cpu_info):
            self.__cpu_infos.add_info(cpu_info)

    def get_cpu_info(self, core_subsets: CoreSubsets) -> CPUInfos:
        """
        :param core_subsets:
        :returns: The CpuInfos for the requested cores.
        """
        with self._collect_responses():
            for core_subset in core_subsets:
                x, y = core_subset.x, core_subset.y
                for p in core_subset.processor_ids:
                    self._send_request(
                        ReadMemory((x, y, 0), get_vcpu_address(p),
                                   CPU_INFO_BYTES),
                        functools.partial(self.__handle_response, x, y, p))

        return self.__cpu_infos
