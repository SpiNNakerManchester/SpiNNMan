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

    def add_processor(self, x, y, processor_id, cpu_info):
        """
        Add a info on a given core.

        :param int x: The x-coordinate of the chip
        :param int y: The y-coordinate of the chip
        :param int processor_id: A processor ID
        :param CPUInfo cpu_info:
            The CPU information for the core.
            Not checked so could be None at test own risk
        """
        self._cpu_infos[x, y, processor_id] = cpu_info

    @property
    def cpu_infos(self):
        """
        The one per core core info.

        :return: iterable of x,y,p core info
        :rtype: iterable(~spinnman.model.CPUInfo)
        """
        return iter(self._cpu_infos.items())

    def __iter__(self):
        return iter(self._cpu_infos)

    def iteritems(self):
        """
        Get an iterable of (x, y, p), cpu_info.
        :rtype: (iterable(tuple(int, int, int),  ~spinnman.model.CPUInfo)
        """
        return iter(self._cpu_infos.items())

    def items(self):
        return self._cpu_infos.items()

    def values(self):
        return self._cpu_infos.values()

    def itervalues(self):
        """
        Get an iterable of cpu_info.
        """
        return iter(self._cpu_infos.items())

    def keys(self):
        return self._cpu_infos.keys()

    def iterkeys(self):
        """
        Get an iterable of (x, y, p).
        """
        return iter(self._cpu_infos.keys())

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

    def __str__(self):
        return str([f"{x}, {y}, {p} (ph: {info.physical_cpu_id})"
                    for (x, y, p), info in self._cpu_infos.items()])

    def __repr__(self):
        return self.__str__()
