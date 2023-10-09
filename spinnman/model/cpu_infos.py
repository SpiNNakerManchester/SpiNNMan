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


class CPUInfos(object):
    """
    A set of CPU information objects.
    """
    __slots__ = [
        "_cpu_infos"]

    def __init__(self):
        self._cpu_infos = dict()

    def add_info(self, cpu_info):
        """
        Add a info on using its core coordinates.

        :param ~spinnman.model.CPUInfo cpu_info:
        """
        self._cpu_infos[cpu_info.x, cpu_info.y, cpu_info.p] = cpu_info

    def add_infos(self, other, states):
        """
        Adds all the infos in the other CPUInfos if the have one of the
        required states

        mainly a support method for Transceiver.add_cpu_information_from_core

        :param CPUInfos other: Another Infos object to merge in
        :param list(~spinnman.model.enums.CPUState) states:
            Only add if the Info has this state
        """
        # pylint: disable=protected-access
        for info in other._cpu_infos:
            if info.state in states:
                self.add_info(other)

    def __iter__(self):
        return iter(self._cpu_infos)

    def __len__(self):
        """
        The total number of processors that are in these core subsets.
        """
        return len(self._cpu_infos)

    def is_core(self, x, y, p):
        """
        Determine if there is a CPU Info for x, y, p.
        """
        return (x, y, p) in self._cpu_infos

    def get_cpu_info(self, x, y, p):
        """
        Get the information for the given core on the given core

        :rtype: CpuInfo
        """
        return self._cpu_infos[x, y, p]

    def infos_for_state(self, state):
        """
        Creates a new CpuInfos object with Just the Infos that match the state.

        :param ~spinnman.model.enums.CPUState state:
        :return: New Infos object with the filtered infos if any
        :rtype: CPUInfo
        """
        for_state = CPUInfos()
        for info in self._cpu_infos.values():
            if info.state == state:
                for_state.add_info(info)
        return for_state

    def get_status_string(self):
        """
        Get a string indicating the status of the given cores.

        :param CPUInfos cpu_infos: A CPUInfos objects
        :rtype: str
        """
        break_down = ""
        for core_info in self._cpu_infos.values():
            break_down += core_info.get_status_string()
        return break_down

    def __str__(self):
        return str([f"{x}, {y}, {p} (ph: {info.physical_cpu_id})"
                    for (x, y, p), info in self._cpu_infos.items()])

    def __repr__(self):
        return self.__str__()
