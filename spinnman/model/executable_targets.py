# Copyright (c) 2016 The University of Manchester
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

from collections import defaultdict
from typing import Collection, Dict, Iterable, Optional, Set, cast
from spinn_utilities.ordered_set import OrderedSet
from spinn_machine import CoreSubsets, FrozenCoreSubsets
from spinnman.exceptions import SpinnmanInvalidParameterException
from .enums import ExecutableType


class ExecutableTargets(object):
    """
    Encapsulate the binaries and cores on which to execute them.
    """
    __slots__ = [
        "_all_core_subsets",
        "_targets",
        "_total_processors",
        "_binary_type_map"]

    __EMPTY_SUBSET = FrozenCoreSubsets()

    def __init__(self) -> None:
        self._targets: Dict[str, CoreSubsets] = dict()
        self._total_processors = 0
        self._all_core_subsets = CoreSubsets()
        self._binary_type_map: Dict[
            ExecutableType, Set[str]] = defaultdict(
                # Need to pretend!
                lambda: cast(Set, OrderedSet()))

    def add_subsets(
            self, binary: str, subsets: CoreSubsets,
            executable_type: Optional[ExecutableType] = None) -> None:
        """
        Add core subsets to a binary.

        :param binary: the path to the binary needed to be executed
        :param subsets:
            the subset of cores that the binary needs to be loaded on
        :param executable_type:
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
            self, binary: str, chip_x: int, chip_y: int, chip_p: int,
            executable_type: Optional[ExecutableType] = None) -> None:
        """
        Add a processor to the executable targets

        :param binary: the binary path for executable
        :param chip_x:
            the coordinate on the machine in terms of x for the chip
        :param chip_y:
            the coordinate on the machine in terms of y for the chip
        :param chip_p: the processor ID to place this executable on
        :param executable_type: the executable type for locating n cores of
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

    def get_n_cores_for_executable_type(
            self, executable_type: ExecutableType) -> int:
        """
        Get the number of cores that the executable type is using.

        :param executable_type:
        :return: the number of cores using this executable type
        """
        return sum(
            len(self.get_cores_for_binary(aplx))
            for aplx in self._binary_type_map[executable_type])

    def get_binaries_of_executable_type(
            self, executable_type: ExecutableType) -> Iterable[str]:
        """
        Get the binaries of a given a executable type.

        :param executable_type: the executable type enum value
        :return: iterable of binaries with that executable type
        """
        return self._binary_type_map[executable_type]

    def executable_types_in_binary_set(self) -> Iterable[ExecutableType]:
        """
        Get the executable types in the set of binaries.

        :return: iterable of the executable types in this binary set.
        """
        return self._binary_type_map.keys()

    def get_cores_for_binary(self, binary: str) -> CoreSubsets:
        """
        Get the cores that a binary is to run on.

        :param binary: The binary to find the cores for
        :returns: A possibly empty CoreSubsets for this binary
        """
        return self._targets.get(binary, self.__EMPTY_SUBSET)

    @property
    def binaries(self) -> Collection[str]:
        """
        The binaries of the executables.
        """
        return self._targets.keys()

    @property
    def total_processors(self) -> int:
        """
        The total number of cores to be loaded.
        """
        return self._total_processors

    @property
    def all_core_subsets(self) -> CoreSubsets:
        """
        All the core subsets for all the binaries.
        """
        return self._all_core_subsets

    def known(
            self, binary: str, chip_x: int, chip_y: int, chip_p: int) -> bool:
        """
        :param binary:
        :param chip_x:
        :param chip_y:
        :param chip_p:
        :returns: True if and only if this chip has this binary
        """
        if not self._all_core_subsets.is_core(chip_x, chip_y, chip_p):
            return False
        # OK if and only if the chip is in this binary already
        if binary in self._targets:
            if self._targets[binary].is_core(chip_x, chip_y, chip_p):
                return True

        raise SpinnmanInvalidParameterException(
            f"x:{chip_x} y:{chip_y} p:{chip_p}", binary,
            "Already associated with a different binary")
