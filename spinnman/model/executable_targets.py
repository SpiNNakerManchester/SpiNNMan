from spinn_front_end_common.utilities import exceptions

from spinn_machine.core_subsets import CoreSubsets

from spinnman.model.enums.executable_start_type import ExecutableStartType

from collections import defaultdict


class ExecutableTargets(object):
    """ Encapsulate the binaries and cores on which to execute them
    """

    def __init__(self):
        self._targets = dict()
        self._total_processors = 0
        self._core_subsets_by_executable_start_type = defaultdict(CoreSubsets)

    def add_binary(self, binary):
        """ Add a binary to the list of things to execute

        :param binary: The binary to add
        """
        if binary not in self._targets:
            self._targets[binary] = CoreSubsets()
        else:
            raise exceptions.ConfigurationException(
                "Binary {} already added".format(binary))

    def has_binary(self, binary):
        """ Determine if the binary is already in the set

        :param binary: The binary to find
        :return: True if the binary exists, false otherwise
        """
        return binary in self._targets

    def add_subsets(self, binary, subsets, binary_start_type):
        """ Add core subsets to a binary

        :param binary: the path to the binary needed to be executed
        :param subsets: the subset of cores that the binary needs to be loaded\
                    on
        :param binary_start_type: the way this binary starts itself.
        :type binary_start_type: enum of type ExecutableStartType
        :return:
        """
        if self.has_binary(binary):
            self._targets[binary].add_core_subset(subsets)
        else:
            self._targets[binary] = subsets

        # verify state enum type
        if not isinstance(binary_start_type, ExecutableStartType):
            raise exceptions.ConfigurationException(
                "The type of binary_start_type must be of "
                "SpinnMan.model.enums.executable_start_type."
                "ExecutableStartType")

        # verify that the executable start type is
        for subset in subsets.core_subsets:
            for p in subset.processor_ids:
                self._total_processors += 1
                self._core_subsets_by_executable_start_type[
                    binary_start_type.value].add_processor(
                        subset.x, subset.y, p)

    def add_processor(self, binary, chip_x, chip_y, chip_p, binary_start_type):
        """ Add a processor to the executable targets

        :param binary: the binary path for executable
        :param chip_x: the coordinate on the machine in terms of x for the chip
        :param chip_y: the coordinate on the machine in terms of y for the chip
        :param chip_p: the processor id to place this executable on
        :param binary_start_type: the way this binary starts itself.
        :type binary_start_type: enum of type ExecutableStartType
        :return:
        """
        if not self.has_binary(binary):
            self.add_binary(binary)
        self._targets[binary].add_processor(chip_x, chip_y, chip_p)

        # verify state enum type
        if not isinstance(binary_start_type, ExecutableStartType):
            raise exceptions.ConfigurationException(
                "The type of binary_start_type must be of "
                "SpinnMan.model.enums.executable_start_type."
                "ExecutableStartType")

        self._core_subsets_by_executable_start_type[binary_start_type.value].\
            add_processor(chip_x, chip_y, chip_p)
        self._total_processors += 1

    def get_cores_for_binary(self, binary):
        """ Get the cores that a binary is to run on

        :param binary: The binary to find the cores for
        """
        if self.has_binary(binary):
            return self._targets[binary]
        else:
            return None

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
        all_core_subsets = CoreSubsets()
        for core_subsets in \
                self._core_subsets_by_executable_start_type.values():
            for subset in core_subsets:
                for p in subset.processor_ids:
                    all_core_subsets.add_processor(subset.x, subset.y, p)
        return all_core_subsets

    def get_start_core_subsets(self, executable_start_type):
        # verify state enum type
        if not isinstance(executable_start_type, ExecutableStartType):
            raise exceptions.ConfigurationException(
                "The type of executable_start_type must be of "
                "SpinnMan.model.enums.executable_start_type."
                "ExecutableStartType")

        return self._core_subsets_by_executable_start_type[
            executable_start_type.value]
