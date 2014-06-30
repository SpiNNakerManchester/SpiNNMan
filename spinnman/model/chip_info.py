class ChipInfo(object):
    """ Information about a chip
    """
    
    def __init__(self, x, y, cores, links, sdram, ip_address=None):
        """
        
        :param x: The x-coordinate of the chip
        :type x: int
        :param y: The y-coordinate of the chip
        :type y: int
        :param cores: iterable of available core ids on the chip
        :type cores: iterable of int
        :param links: iterable of available links outgoing from the chip
        :type links: iterable of :py:class:`spinnman.model.link_info.LinkInfo`
        :param sdram: The size of the shared sdram on the chip in bytes
        :type sdram: int
        :param ip_address: The ip address of the ethernet adapter of the chip\
                    or None if there is no ethernet adapter on the chip
        :type ip_address: str
        :raise None: No known exceptions are raised
        """
        pass
    
    @property
    def x(self):
        """ The x-coordinate of the chip
        
        :return: The x-coordinate
        :rtype: int
        """
        pass
    
    @property
    def y(self):
        """ The y-coordinate of the chip
        
        :return: The y-coordinate
        :rtype: int
        """
        pass
    
    @property
    def cores(self):
        """ An iterable of the ids of the cores of the chip
        
        :return: An iterable of core ids
        :rtype: iterable of int
        """
        pass
    
    @property
    def links(self):
        """ An iterable of the links coming out of the chip
        
        :return: An iterable of links
        :rtype: iterable of spinnman.model.link_info.LinkInfo
        """
        pass
    
    @property
    def sdram(self):
        """ The amount of SDRAM on the chip in bytes
        
        :return: The size of the SDRAM
        :rtype: int
        """
        pass
    
    @property
    def ip_address(self):
        """ The ip address of the ethernet adapter of the chip if there is one
        
        :return: The ip address, or None if there is no ethernet adaptor
        :rtype: str
        """
        pass
