# Copyright (c) 2017-2019 The University of Manchester
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from collections import OrderedDict


class CPUInfos(object):
    """ A set of CPU information objects.
    """
    __slots__ = [
        "_cpu_infos"]

    def __init__(self):
        self._cpu_infos = OrderedDict()

    def add_processor(self, x, y, processor_id, cpu_info):
        """ Add a processor on a given chip to the set.

        :param int x: The x-coordinate of the chip
        :param int y: The y-coordinate of the chip
        :param int processor_id: A processor ID
        :param CPUInfo cpu_info: The CPU information for the core
        """
        self._cpu_infos[x, y, processor_id] = cpu_info

    @property
    def cpu_infos(self):
        """ The one per core core info.

        :return: iterable of x,y,p core info
        """
        return iter(self._cpu_infos.items())

    def __iter__(self):
        return iter(self._cpu_infos)

    def iteritems(self):
        """ Get an iterable of (x, y, p), cpu_info
        """
        return iter(self._cpu_infos.items())

    def items(self):
        return self._cpu_infos.items()

    def values(self):
        return self._cpu_infos.values()

    def itervalues(self):
        """ Get an iterable of cpu_info.
        """
        return iter(self._cpu_infos.items())

    def keys(self):
        return self._cpu_infos.keys()

    def iterkeys(self):
        """ Get an iterable of (x, y, p).
        """
        return iter(self._cpu_infos.keys())

    def __len__(self):
        """ The total number of processors that are in these core subsets.
        """
        return len(self._cpu_infos)

    def is_core(self, x, y, p):
        """ Determine if there is a CPU Info for x, y, p
        """
        return (x, y, p) in self._cpu_infos

    def get_cpu_info(self, x, y, p):
        """ Get the information for the given core on the given chip
        """
        return self._cpu_infos[x, y, p]

    def __str__(self):
        return str(self._cpu_infos.keys())

    def __repr__(self):
        return self.__str__()
