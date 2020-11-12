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

from collections import defaultdict
from spinn_utilities.ordered_set import OrderedSet
from spinn_machine import CoreSubsets
from spinnman.exceptions import SpinnmanInvalidParameterException


class ExecutableTargets(object):
    """ Encapsulate the binaries and cores on which to execute them.
    """
    __slots__ = [
        "_all_core_subsets",
        "_targets",
        "_total_processors",
        "_binary_type_map"]

    def __init__(self):
        self._targets = dict()
        self._total_processors = 0
        self._all_core_subsets = CoreSubsets()
        self._binary_type_map = defaultdict(OrderedSet)

    def add_subsets(self, binary, subsets, executable_type=None):
        """ Add core subsets to a binary

        :param str binary: the path to the binary needed to be executed
        :param ~spinn_machine.CoreSubsets subsets:
            the subset of cores that the binary needs to be loaded on
        :param ~spinn_front_end_common.utilities.utility_objs.ExecutableType \
                executable_type:
            The type of this executable.
            ``None`` means don't record it.
        """
        try:
            for subset in subsets.core_subsets:
                for p in subset.processor_ids:
                    self.add_processor(binary, subset.x, subset.y, p)
        except AttributeError:
            if subsets is not None:
                raise
        if executable_type is not None:
            self._binary_type_map[executable_type].add(binary)

    def add_processor(
            self, binary, chip_x, chip_y, chip_p, executable_type=None):
        """ Add a processor to the executable targets

        :param str binary: the binary path for executable
        :param int chip_x:
            the coordinate on the machine in terms of x for the chip
        :param int chip_y:
            the coordinate on the machine in terms of y for the chip
        :param int chip_p: the processor ID to place this executable on
        :param ~spinn_front_end_common.utilities.utility_objs.ExecutableType \
                executable_type:
            the executable type for locating n cores of
        """
        if self.known(binary, chip_x, chip_y, chip_p):
            return
        if binary not in self._targets:
            self._targets[binary] = CoreSubsets()
        if executable_type is not None:
            self._binary_type_map[executable_type].add(binary)
        self._targets[binary].add_processor(chip_x, chip_y, chip_p)
        self._all_core_subsets.add_processor(chip_x, chip_y, chip_p)
        self._total_processors += 1

    def get_n_cores_for_executable_type(self, executable_type):
        """ get the number of cores that the executable type is using

        :param ~spinn_front_end_common.utilities.utility_objs.ExecutableType \
                executable_type:
            the executable type for locating n cores of
        :return: the number of cores using this executable type
        :rtype: int
        """
        return sum(
            len(self.get_cores_for_binary(aplx))
            for aplx in self._binary_type_map[executable_type])

    def get_binaries_of_executable_type(self, executable_type):
        """ get the binaries of a given a executable type

        :param ~spinn_front_end_common.utilities.utility_objs.ExecutableType \
                executable_type:
            the executable type enum value
        :return: iterable of binaries with that executable type
        :rtype: iterable(str)
        """
        return self._binary_type_map[executable_type]

    def executable_types_in_binary_set(self):
        """ get the executable types in the set of binaries

        :return: iterable of the executable types in this binary set.
        :rtype:
            iterable(~spinn_front_end_common.utilities.utility_objs.ExecutableType)
        """
        return self._binary_type_map.keys()

    def get_cores_for_binary(self, binary):
        """ Get the cores that a binary is to run on

        :param str binary: The binary to find the cores for
        """
        return self._targets.get(binary)

    @property
    def binaries(self):
        """ The binaries of the executables

        :rtype: iterable(str)
        """
        return self._targets.keys()

    @property
    def total_processors(self):
        """ The total number of cores to be loaded

        :rtype: int
        """
        return self._total_processors

    @property
    def all_core_subsets(self):
        """ All the core subsets for all the binaries

        :rtype: ~spinn_machine.CoreSubsets
        """
        return self._all_core_subsets

    def known(self, binary, chip_x, chip_y, chip_p):
        """
        :param str binary:
        :param int chip_x:
        :param int chip_y:
        :param int chip_p:
        :rtype: bool
        """
        if not self._all_core_subsets.is_core(chip_x, chip_y, chip_p):
            return False
        # OK if and only if the chip is in this binary already
        if binary in self._targets:
            if self._targets[binary].is_core(chip_x, chip_y, chip_p):
                return True

        parameter = "x:{} y:{} p:{}".format(chip_x, chip_y, chip_p)
        problem = "Already associated with a different binary"
        raise SpinnmanInvalidParameterException(parameter, binary, problem)
