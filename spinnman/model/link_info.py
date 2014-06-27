class LinkInfo(object):
    """ Information about a link between chips
    """
    
    def __init__(self, x_src, y_src, src_link_id, x_dest, y_dest, default_from,
            default_to):
        """
        :param x_src: The x-coordinate of the source chip of the link
        :type x_src: int
        :param y_src: The y-coordinate of the source chip of the link
        :type y_src: int
        :param src_link_id: The unique identifier of the link on the source\
                    chip
        :type src_link_id: int
        :param x_dest: The x-coordinate of the destination chip of the link, or\
                    None if this link does not connect to a chip (e.g. the\
                    destination is a connected peripheral)
        :type x_dest: int
        :param y_dest: The y-coordinate of the destination chip of the link, or\
                    None if this link does not connect to a chip (e.g. the\
                    destination is a connected peripheral)
        :type y_dest: int
        :param default_from: The id of the link on the source chip for which,\
                    if a message is received on that link, and no entry for the\
                    message exists in the routing table of the chip, the packet\
                    will be sent down this link; None if that link is not\
                    enabled
        :type default_from: int
        :param default_to: The id of the link on the source chip for which, if\
                    a message is received on this link, and no entry for the\
                    message exists in the routing table of the chip, the packet\
                    will be sent down that link; None if that link is not\
                    enabled
        :type default_to: int
        :raise None: No known exceptions are raised
        """
        pass
    
    @property
    def x_src(self):
        """ The x-coordinate of the source chip of the link
        
        :return: The x-coordinate
        :rtype: int
        """
        pass
    
    @property
    def y_src(self):
        """ The y-coordinate of the source chip of the link
        
        :return: The y-coordinate
        :rtype: int
        """
        pass
    
    @property
    def src_link_id(self):
        """ The unique id of the link on the source chip
        
        :return: The unique id
        :rtype: int
        """
        pass
    
    @property
    def x_dest(self):
        """ The x-coordinate of the destination chip of the link
        
        :return: The x-coordinate, or None if the destination is not a chip
        :rtype: int
        """
        pass
    
    @property
    def y_dest(self):
        """ The y-coordinate of the destination chip of the link
        
        :return: The y-coordinate, or None if the destination is not a chip
        :rtype: int
        """
        pass
    
    @property
    def default_from(self):
        """ The id of the link from which this link is the default outgoing\
            route
        
        :return: The id of the link, or None if this link is not the default\
                    of any other link
        :rtype: int
        """
        pass
    
    @property
    def default_to(self):
        """ The id of the link which is the default outgoing route for this\
            link
            
        :return: The id of the link, or None if there is no default link\
                    for this link
        :rtype: int
        """
        pass
