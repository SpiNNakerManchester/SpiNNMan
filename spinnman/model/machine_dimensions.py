class MachineDimensions(object):
    """ Represents the dimensions of a machine
    """
    
    def __init__(self, x_max, y_max):
        """
        :param x_max: The maximum x-coordinate of the chips in the machine
        :type x_max: int
        :param y_max: The maximum y-coordinate of the chips in the machine
        :type y_max: int
        :raise None: No known exceptions are raised
        """
        self._x_max = x_max
        self._y_max = y_max
    
    @property
    def x_max(self):
        """ The maximum x-coordinate of the chips in the machine
        
        :return: The x-coordinate
        :rtype: int
        """
        return self._x_max
    
    @property
    def y_max(self):
        """ The maximum y-coordinate of the chips in the machine
        
        :return: The y-coordinate
        :rtype: int
        """
        return self._y_max
