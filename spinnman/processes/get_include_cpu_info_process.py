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
    """
    Gets the CPU for processors over the provided connection.

    This class returns only infos for the requested states.
    """
    __slots__ = ("__states", )

    def __init__(self, connection_selector: ConnectionSelector,
                 states: Container[CPUState]):
        """
        :param connection_selector:
        :param states:
            The states for which info is required.
        """
        super().__init__(connection_selector)
        self.__states = states

    @overrides(GetCPUInfoProcess._is_desired)
    def _is_desired(self, cpu_info: CPUInfo) -> bool:
        return cpu_info.state in self.__states
