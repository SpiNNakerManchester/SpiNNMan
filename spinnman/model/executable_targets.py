from spinn_machine import CoreSubsets


class ExecutableTargets(object):
    """ Encapsulate the binaries and cores on which to execute them
    """

    def __init__(self):
        self._targets = dict()
        self._total_processors = 0
        self._all_core_subsets = CoreSubsets()

    def add_subsets(self, binary, subsets):
        """ Add core subsets to a binary

        :param binary: the path to the binary needed to be executed
        :param subsets: the subset of cores that the binary needs to be loaded\
                    on
        :return:
        """
        if binary in self._targets:
            self._targets[binary].add_core_subset(subsets)
        else:
            self._targets[binary] = subsets

        for subset in subsets.core_subsets:
            for p in subset.processor_ids:
                self._total_processors += 1
                self._all_core_subsets.add_processor(subset.x, subset.y, p)

    def add_processor(self, binary, chip_x, chip_y, chip_p):
        """ Add a processor to the executable targets

        :param binary: the binary path for executable
        :param chip_x: the coordinate on the machine in terms of x for the chip
        :param chip_y: the coordinate on the machine in terms of y for the chip
        :param chip_p: the processor id to place this executable on
        :return:
        """
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
