class IOBuffer(object):
    """ The contents of IOBUF for a core
    """
    
    def __init__(self, x, y, p, iobuf):
        """
        :param x: The x-coordinate of a chip
        :type x: int
        :param y: The y-coordinate of a chip
        :type y: int
        :param p: The p-coordinate of a chip
        :type p: int
        :param iobuf: The contents of the buffer for the chip
        :type iobuf: str
        :raise None: No known exceptions are raised
        """
    
    @property
    def x(self):
        """ The x-coordinate of the chip containing the core
        
        :return: The x-coordinate of the chip
        :rtype: int
        """
        pass
    
    @property
    def y(self):
        """ The y-coordinate of the chip containing the core
        
        :return: The y-coordinate of the chip
        :rtype: int
        """
        pass
    
    @property
    def p(self):
        """ The id of the core on the chip
        
        :return: The id of the core
        :rtype: int
        """
        pass
    
    @property
    def iobuf(self):
        """ The contents of the buffer
        
        :return: The contents of the buffer
        :rtype: str
        """
        pass