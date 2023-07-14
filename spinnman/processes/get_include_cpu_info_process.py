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

from spinnman.model import CPUInfo
from spinnman.model.enums import CPUState
from .get_cpu_info_process import GetCPUInfoProcess


class GetIncludeCPUInfoProcess(GetCPUInfoProcess):
    __slots__ = [
        "_states"]

    def __init__(self, connection_selector, states):
        """
        :param connection_selector:
        :type connection_selector:
            AbstractMultiConnectionProcessConnectionSelector
        """
        super().__init__(connection_selector)
        self._states = states

    def _filter_and_add_repsonse(self, x, y, p, cpu_data):
        state = CPUState(cpu_data[6])
        if state in self._states:
            self._cpu_infos.add_info(CPUInfo(x, y, p, cpu_data))
