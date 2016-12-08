from collections import OrderedDict
from spinn_machine.core_subset import CoreSubset

class CoreInfoSubsets(object):
    """
    encpasulation of core subsets and core info subsets
    """

    def __init__(self):
        self._core_infos = OrderedDict()
        self._core_subsets = OrderedDict()

    def _add_core_subset(self, core_subset):
        """ Add a core subset to the set

        :param core_subset: The core subset to add
        :type core_subset: :py:class:`spinn_machine.core_subset.CoreSubset`
        :return: Nothing is returned
        :rtype: None
        """
        self._core_subsets[(core_subset.x, core_subset.y)] = core_subset

    def add_processor(self, x, y, processor_id, core_info):
        """ Add a processor on a given chip to the set

        :param x: The x-coordinate of the chip
        :type x: int
        :param y: The y-coordinate of the chip
        :type y: int
        :param processor_id: A processor id
        :type processor_id: int
        :return: Nothing is returned
        :rtype: None
        """
        if (x, y) not in self._core_subsets:
            self._add_core_subset(CoreSubset(x, y, []))
        self._core_subsets[(x, y)].add_processor(processor_id)
        self._core_infos[(x, y, processor_id)] = core_info

    @property
    def core_subsets(self):
        """ The one-per-chip subsets

        :return: Iterable of core subsets
        :rtype: iterable of :py:class:`spinn_machine.core_subset.CoreSubset`
        """
        return self._core_subsets.itervalues()

    @property
    def core_infos(self):
        """ the one per core core info

        :return: iterable of x,y,p core info
        """
        return self._core_infos.iteritems()

    def get_core_subset_for_chip(self, x, y):
        """ Get the core subset for a chip

        :param x: The x-coordinate of a chip
        :type x: int
        :param y: The y-coordinate of a chip
        :type y: int
        :return: The core subset of a chip, which will be empty if not added
        :rtype: :py:class:`spinn_machine.core_subset.CoreSubset`
        """
        if (x, y) not in self._core_subsets:
            return CoreSubset(x, y, [])
        return self._core_subsets[(x, y)]

    def __len__(self):
        """ The total number of processors that are in these core subsets
        """
        counter = 0
        for (x, y) in self._core_subsets:
            counter += len(self._core_subsets[(x, y)])
        return counter



