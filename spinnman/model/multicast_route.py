class MulticastRoute(object):
    """ Represents a multicast route
    """
    
    def __init__(self, key, mask, route):
        """
        
        :param key: The routing key
        :type key: int
        :param mask: The route key mask
        :type mask: int
        :param route: The route, as a spinnaker bit mask
        :type route: int
        :raise None: No known exceptions are raised
        """
        pass
    
    @property
    def key(self):
        """ The routing key
        
        :return: The routing key
        :rtype: int
        """
        pass
    
    @property
    def mask(self):
        """ The routing mask
        
        :return: The routing mask
        :rtype: int
        """
        pass
    
    @property
    def route(self):
        """ The route as a bitmask of |16 core bits|6 link bits|
        
        :return: The route
        :rtype: int
        """
        pass
