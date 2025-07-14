# Copyright (c) 2017 The University of Manchester
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

from typing import Dict, Iterable, Iterator
from typing_extensions import Self
from spinn_utilities.typing.coords import XYP
from spinnman.model.enums import CPUState
from .cpu_info import CPUInfo


class CPUInfos(object):
    """
    A set of CPU information objects.
    """
    __slots__ = [
        "_cpu_infos"]

    def __init__(self) -> None:
        self._cpu_infos: Dict[XYP, CPUInfo] = dict()

    def add_info(self, cpu_info: CPUInfo) -> None:
        """
        Add a info on using its core coordinates.

        :param cpu_info:
        """
        self._cpu_infos[cpu_info.x, cpu_info.y, cpu_info.p] = cpu_info

    def add_infos(self, other: Self, states: Iterable[CPUState]) -> None:
        """
        Adds all the infos in the other CPUInfos if the have one of the
        required states

        mainly a support method for Transceiver.add_cpu_information_from_core

        :param other: Another Infos object to merge in
        :param states: Only add if the Info has this state
        """
        # pylint: disable=protected-access
        assert isinstance(other, CPUInfos)
        for info in other._cpu_infos.values():
            if info.state in states:
                self.add_info(info)

    def __iter__(self) -> Iterator[XYP]:
        return iter(self._cpu_infos)

    def __len__(self) -> int:
        """
        The total number of processors that are in these core subsets.
        """
        return len(self._cpu_infos)

    def is_core(self, x: int, y: int, p: int) -> bool:
        """
        :returns: If there is a CPU Info for x, y, p.
        """
        return (x, y, p) in self._cpu_infos

    def get_cpu_info(self, x: int, y: int, p: int) -> CPUInfo:
        """
        :returns: The information for the given core on the given core
        """
        return self._cpu_infos[x, y, p]

    def infos_for_state(self, state: CPUState) -> 'CPUInfos':
        """
        Creates a new CpuInfos object with Just the Infos that match the state.

        :param state:
        :return: New Infos object with the filtered infos if any
        """
        for_state = CPUInfos()
        for info in self._cpu_infos.values():
            if info.state == state:
                for_state.add_info(info)
        return for_state

    def infos_not_in_states(self, states: Iterable[CPUState]) -> 'CPUInfos':
        """
        Creates a new CpuInfos object with Just the Infos that match the state.

        :param states:
        :return: New Infos object with the filtered infos if any
        """
        for_state = CPUInfos()
        for info in self._cpu_infos.values():
            if info.state not in states:
                for_state.add_info(info)
        return for_state

    def get_status_string(self) -> str:
        """
        :returns: A string indicating the status of the given cores.
        """
        break_down = ""
        for core_info in self._cpu_infos.values():
            break_down += core_info.get_status_string()
        return break_down

    def __str__(self) -> str:
        return str([f"{x}, {y}, {p} (ph: {info.physical_cpu_id})"
                    for (x, y, p), info in self._cpu_infos.items()])

    def __repr__(self) -> str:
        return self.__str__()
