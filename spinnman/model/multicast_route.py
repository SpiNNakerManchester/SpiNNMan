class MulticastRoute(object):
    """ Represents a multicast route
    """
    
    def __init__(self, key, mask, processor_ids, link_ids):
        """
        
        :param key: The routing key
        :type key: int
        :param mask: The route key mask
        :type mask: int
        :param processor_ids: The destination processor ids
        :type processor_ids: iterable of int
        :param link_ids: The destination link ids
        :type link_ids: iterable of int
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
    def processor_ids(self):
        """ The destination processor ids
        
        :return: An iterable of processor ids
        :rtype: iterable of int
        """
        pass
    
    @property
    def link_ids(self):
        """ The destination link ids
        
        :return: An iterable of link ids
        :rtype: iterable of int
        """
        pass
