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

from spinn_machine import CoreSubsets
from spinnman.exceptions import SpinnmanInvalidParameterException


class ExecutableTargets(object):
    """ Encapsulate the binaries and cores on which to execute them.
    """
    __slots__ = [
        "_all_core_subsets",
        "_targets",
        "_total_processors"]

    def __init__(self):
        self._targets = dict()
        self._total_processors = 0
        self._all_core_subsets = CoreSubsets()

    def add_subsets(self, binary, subsets):
        """ Add core subsets to a binary

        :param binary: the path to the binary needed to be executed
        :param subsets: \
            the subset of cores that the binary needs to be loaded on
        :return:
        """
        for subset in subsets.core_subsets:
            for p in subset.processor_ids:
                self.add_processor(binary, subset.x, subset.y, p)

    def add_processor(self, binary, chip_x, chip_y, chip_p):
        """ Add a processor to the executable targets

        :param binary: the binary path for executable
        :param chip_x: the coordinate on the machine in terms of x for the chip
        :param chip_y: the coordinate on the machine in terms of y for the chip
        :param chip_p: the processor ID to place this executable on
        :return:
        """
        if self.known(binary, chip_x, chip_y, chip_p):
            return
        if binary not in self._targets:
            self._targets[binary] = CoreSubsets()
        self._targets[binary].add_processor(chip_x, chip_y, chip_p)
        self._all_core_subsets.add_processor(chip_x, chip_y, chip_p)
        self._total_processors += 1

    def get_cores_for_binary(self, binary):
        """ Get the cores that a binary is to run on

        :param binary: The binary to find the cores for
        """
        return self._targets.get(binary)

    @property
    def binaries(self):
        """ The binaries of the executables
        """
        return self._targets.keys()

    @property
    def total_processors(self):
        """ The total number of cores to be loaded
        """
        return self._total_processors

    @property
    def all_core_subsets(self):
        """ All the core subsets for all the binaries
        """
        return self._all_core_subsets

    def known(self, binary, chip_x, chip_y, chip_p):
        if self._all_core_subsets.is_core(chip_x, chip_y, chip_p):
            # OK if and only if the chip is in this binary already
            if binary in self._targets:
                if self._targets[binary].is_core(chip_x, chip_y, chip_p):
                    return True
            parameter = "x:{} y:{} p:{}".format(chip_x, chip_y, chip_p)
            problem = "Already associated with a different binary"
            raise SpinnmanInvalidParameterException(parameter, binary, problem)
        else:
            return False
