from collections import OrderedDict


class CPUInfos(object):
    """ A set of CPU information objects
    """

    def __init__(self):
        self._cpu_infos = OrderedDict()

    def add_processor(self, x, y, processor_id, cpu_info):
        """ Add a processor on a given chip to the set

        :param x: The x-coordinate of the chip
        :type x: int
        :param y: The y-coordinate of the chip
        :type y: int
        :param processor_id: A processor id
        :type processor_id: int
        :param cpu_info: The CPU information for the core
        :type cpu_info: :py:class:`spinnman.model.enums.cpu_info.CPUInfo`
        """
        self._cpu_infos[x, y, processor_id] = cpu_info

    @property
    def cpu_infos(self):
        """ the one per core core info

        :return: iterable of x,y,p core info
        """
        return self._cpu_infos.iteritems()

    def __iter__(self):
        return self._cpu_infos.__iter__()

    def iteritems(self):
        """ Get an iterable of (x, y, p), cpu_info
        """
        return self._cpu_infos.iteritems()

    def itervalues(self):
        """ Get an iterable of cpu_info
        """
        return self._cpu_infos.itervalues()

    def iterkeys(self):
        """ Get an iterable of (x, y, p)
        """
        return self._cpu_infos.iterkeys()

    def __len__(self):
        """ The total number of processors that are in these core subsets
        """
        return len(self._cpu_infos)
