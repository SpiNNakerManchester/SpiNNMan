class MulticastMessage(object):
    """ A SpiNNaker Multicast message
    """
    
    def __init__(self, key, payload=None):
        """ 
        :param key: The key of the packet
        :type key: int
        :param payload: The optional payload of the packet
        :type payload: int
        :raise None: No known exceptions are raised
        """
        pass
    
    @property
    def key(self):
        """ The key of the packet
        
        :return: The key
        :rtype: int
        """
        pass
    
    @property
    def payload(self):
        """ The payload of the packet if there is one
        
        :return: The payload, or None if there is no payload
        :rtype: int
        """
        pass
