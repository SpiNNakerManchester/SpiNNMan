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

from typing import Container
from spinn_utilities.overrides import overrides
from spinnman.model import CPUInfo
from spinnman.model.enums import CPUState
from .abstract_multi_connection_process_connection_selector import (
    ConnectionSelector)
from .get_cpu_info_process import GetCPUInfoProcess


class GetIncludeCPUInfoProcess(GetCPUInfoProcess):
    __slots__ = ("__states", )

    def __init__(self, connection_selector: ConnectionSelector,
                 states: Container[CPUState]):
        """
        :param connection_selector:
        :type connection_selector:
            AbstractMultiConnectionProcessConnectionSelector
        """
        super().__init__(connection_selector)
        self.__states = states

    @overrides(GetCPUInfoProcess._filter_and_add_repsonse)
    def _filter_and_add_repsonse(
            self, x: int, y: int, p: int, cpu_data: bytes):
        state = CPUState(cpu_data[6])
        if state in self.__states:
            self._cpu_infos.add_info(CPUInfo(x, y, p, cpu_data))
