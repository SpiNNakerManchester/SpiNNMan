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
        self._processor_ids = processor_ids

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
        return self._processor_ids
