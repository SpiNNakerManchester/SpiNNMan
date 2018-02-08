from collections import defaultdict
from spinn_machine import CoreSubsets


class ExecutableTargets(object):
    """ Encapsulate the binaries and cores on which to execute them
    """

    __slots__ = (
        # the targets
        "_targets",

        # the total number of processors used
        "_total_processors",

        # the total core subsets
        "_all_core_subsets",

        # the mapping between binary and executable type
        "_binary_to_executable_types_map"
    )

    def __init__(self):
        self._targets = dict()
        self._total_processors = 0
        self._all_core_subsets = CoreSubsets()
        self._binary_to_executable_types_map = defaultdict(list)

    def add_subsets(self, binary, subsets, executable_type):
        """ Add core subsets to a binary

        :param binary: the path to the binary needed to be executed
        :param subsets: the subset of cores that the binary needs to be loaded\
                    on
        :param executable_type: the executable type of the binary
        :rtype: None
        """
        if binary in self._targets:
            self._targets[binary].add_core_subset(subsets)
        else:
            self._targets[binary] = subsets

        for subset in subsets.core_subsets:
            for p in subset.processor_ids:
                self._total_processors += 1
                self._all_core_subsets.add_processor(subset.x, subset.y, p)

        # add to binary to executable type
        self._binary_to_executable_types_map[executable_type].append(binary)

    def add_processor(self, binary, chip_x, chip_y, chip_p, executable_type):
        """ Add a processor to the executable targets

        :param binary: the binary path for executable
        :param chip_x: the coordinate on the machine in terms of x for the chip
        :param chip_y: the coordinate on the machine in terms of y for the chip
        :param chip_p: the processor id to place this executable on
        :param executable_type: the executable type of the binary
        :rtype: None
        """
        if binary not in self._targets:
            self._targets[binary] = CoreSubsets()
        self._targets[binary].add_processor(chip_x, chip_y, chip_p)
        self._all_core_subsets.add_processor(chip_x, chip_y, chip_p)
        self._total_processors += 1

        # add to binary to executable type
        if binary not in self._binary_to_executable_types_map[executable_type]:
            self._binary_to_executable_types_map[executable_type].append(
                binary)

    def get_n_cores_for_executable_type(self, executable_type):
        """ returns the number of cores that the executable type is using
        
        :param executable_type: the executable type for locating n cores of
        :return:  the number of cores using this executable type
        """
        count = 0
        for binary in self._binary_to_executable_types_map[executable_type]:
            count += len(self.get_cores_for_binary(binary))
        return count

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

    def get_binaries_of_executable_type(self, execute_type):
        """ method for extracting the binaries of a given a executable type
        
        :param execute_type: 
        :return: a list of binaries with that executable type
        """
        return self._binary_to_executable_types_map[execute_type]

    def executable_types_in_binary_set(self):
        """ method for getting the executable types that are in the set of\
         binaries
        
        :return: list of the executable types in this binary set. 
        """
        return self._binary_to_executable_types_map.keys()

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
