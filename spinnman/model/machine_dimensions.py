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
        pass
    
    @property
    def x_max(self):
        """ The maximum x-coordinate of the chips in the machine
        
        :return: The x-coordinate
        :rtype: int
        """
        pass
    
    @property
    def y_max(self):
        """ The maximum y-coordinate of the chips in the machine
        
        :return: The y-coordinate
        :rtype: int
        """
        pass
