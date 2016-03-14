from spinnman.exceptions import SpinnmanInvalidParameterException


class CoreSubset(object):
    """ Represents a subset of the cores on a chip
    """

    def __init__(self, x, y, processor_ids):
        """
        :param x: The x-coordinate of the chip
        :type x: int
        :param y: The y-coordinate of the chip
        :type y: int
        :param processor_ids: An iterable of processor ids on the chip
        :type processor_ids: iterable of int
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If there\
                    is more than one core listed with the same id
        """
        self._x = x
        self._y = y
        self._processor_ids = set()
        for processor_id in processor_ids:
            self.add_processor(processor_id)

    def add_processor(self, processor_id):
        """ Adds a processor id to this subset

        :param processor_ids: A processor id
        :type processor_ids: int
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If there\
                    is already a processor in the subset with the same id
        """
        if processor_id in self._processor_ids:
            raise SpinnmanInvalidParameterException(
                "processor_ids", processor_id,
                "Each processor id must only occur once")

        self._processor_ids.add(processor_id)

    def __contains__(self, processor_id):
        return processor_id in self._processor_ids

    @property
    def x(self):
        """ The x-coordinate of the chip

        :return: The x-coordinate
        :rtype: int
        """
        return self._x

    @property
    def y(self):
        """ The y-coordinate of the chip

        :return: The y-coordinate
        :rtype: int
        """
        return self._y

    @property
    def processor_ids(self):
        """ The subset of processor ids on the chip

        :return: An iterable of processor ids
        :rtype: iterable of int
        """
        return iter(self._processor_ids)

    def __repr__(self):
        return "{}:{}:{}".format(self._x, self._y, self._processor_ids)

    def __eq__(self, other):
        if isinstance(other, CoreSubset):
            if (self.x != other.x or self._y != other.y or
                    self._processor_ids != other.processor_ids):
                return False
            else:
                return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        processors = frozenset(self._processor_ids)
        return (self._x, self._y, processors).__hash__()

    def __len__(self):
        """ The number of processors in this core subset
        """
        return len(self._processor_ids)
