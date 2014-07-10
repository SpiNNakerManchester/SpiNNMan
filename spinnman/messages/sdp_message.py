from spinnman.exceptions import SpinnmanInvalidParameterException


class SDPMessage(object):
    """ Wraps up an SDP message.  Each parameter of the message can be set\
        once, after which it is immutable.  It is an error to set a parameter\
        that has already been set.
    """
    
    def __init__(self, flags, destination_port, destination_chip_x, 
            destination_chip_y, destination_cpu, tag=None, source_port=None,
            source_chip_x=None, source_chip_y=None, source_cpu=None, data=None):
        """
        :param flags: Any flags for the packet
        :type flags: :py:class:`spinnman.messages.sdp_flag.SDPFlag`
        :param destination_port: The destination port of the packet between 0\
                    and 7
        :type destination_port: int
        :param destination_chip_x: The x-coordinate of the destination chip\
                    between 0 and 255
        :type destination_chip_x: int
        :param destination_chip_y: The y-coordinate of the destination chip\
                    between 0 and 255
        :type destination_chip_y: int
        :param destination_cpu: The destination processor id within the chip\
                    between 0 and 31
        :type destination_cpu: int
        :param tag: The ip tag of the packet between 0 and 255, or None if it\
                    is to be set later
        :type tag: int
        :param source_port: The source port of the packet between 0 and 7, or\
                    None if it is to be set later
        :type source_port: int
        :param source_chip_x: The x-coordinate of the source chip\
                    between 0 and 255, or None if it is to be set later
        :type source_chip_x: int
        :param source_chip_y: The y-coordinate of the source chip\
                    between 0 and 255, or None if it is to be set later
        :param source_cpu: The source processor id within the chip\
                   between 0 and 31, or None if it is to be set later
        :type source_cpu: int
        :param data: The data of the SDP packet, or None if no data
        :type data: bytearray
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If one of\
                    the parameters is not valid
        """
        if destination_port < 0 or destination_port > 7:
            raise SpinnmanInvalidParameterException(
                    "destination_port", str(destination_port),
                    "Must be between 0 and 7")
        if destination_chip_x < 0 or destination_chip_x > 255:
            raise SpinnmanInvalidParameterException(
                    "destination_chip_x", str(destination_chip_x),
                    "Must be between 0 and 255")
        if destination_chip_y < 0 or destination_chip_y > 255:
            raise SpinnmanInvalidParameterException(
                    "destination_chip_y", str(destination_chip_y),
                    "Must be between 0 and 255")
        if destination_cpu < 0 or destination_cpu > 31:
            raise SpinnmanInvalidParameterException(
                    "destination_cpu", str(destination_cpu),
                    "Must be between 0 and 31")
        
        self._flags = flags
        self._destination_port = destination_port
        self._destination_chip_x = destination_chip_x
        self._destination_chip_y = destination_chip_y
        self._destination_cpu = destination_cpu
        self._tag = None
        self._source_port = None
        self._source_chip_x = None
        self._source_chip_y = None
        self._source_cpu = None
        self._data = data
        
        self.tag = tag
        self.source_port = source_port
        self.source_chip_x = source_chip_x
        self.source_chip_y = source_chip_y
        self.source_cpu = source_cpu
    
    @property
    def flags(self):
        """ The flags of the packet
        
        :return: The flags of the packet
        :rtype: :py:class:`spinnman.messages.sdp_flag.SDPFlag`
        """
        return self._flags
    
    @property
    def destination_port(self):
        """ The destination port of the packet
        
        :return: The destination port of the packet between 0 and 7
        :rtype: int
        """
        return self._destination_port
        
    @property
    def destination_chip_x(self):
        """ The x-coordinate of the destination chip of the packet
        
        :return: The x-coordinate of the chip, between 0 and 255
        :rtype: int
        """
        return self._destination_chip_x
    
    @property  
    def destination_chip_y(self):
        """ The y-coordinate of the destination chip of the packet
        
        :return: The y-coordinate of the chip, between 0 and 255
        :rtype: int
        """
        return self._destination_chip_y
    
    @property
    def destination_cpu(self):
        """ The core on the destination chip
        
        :return: The core on the destination chip, between 0 and 31
        :rtype: int 
        """
        return self._destination_cpu
    
    @property
    def tag(self):
        """ The tag of the packet
        
        :return: The tag of the packet between 0 and 255
        :rtype: int
        """
        return self._tag
    
    @tag.setter
    def tag(self, tag):
        """ Set the tag of the packet
        
        :param tag: The tag to set, between 0 and 255
        :type tag: int
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If the\
                    tag has already been set or if the value is out of range
        """
        if self._tag is not None:
            raise SpinnmanInvalidParameterException(
                    "tag", str(tag), "Already set")
        if tag is not None and (tag < 0 or tag > 255):
            raise SpinnmanInvalidParameterException(
                    "tag", str(tag), "Must be between 0 and 255")
            
        self._tag = tag
    
    @property
    def source_port(self):
        """ The source port of the packet
        
        :return: The source port of the packet between 0 and 7
        :rtype: int
        """
        return self._source_port
    
    @source_port.setter
    def source_port(self, source_port):
        """ Set the source port of the packet
        
        :param source_port: The source port to set, between 0 and 7
        :type source_port: int
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If the\
                    source_port has already been set or if the value is out of\
                    range
        """
        if self._source_port is not None:
            raise SpinnmanInvalidParameterException(
                    "source_port", str(source_port), "Already set")
        if source_port is not None and (source_port < 0 or source_port > 7):
            raise SpinnmanInvalidParameterException(
                    "source_port", str(source_port), "Must be between 0 and 7")
            
        self._source_port = source_port
        
    @property
    def source_chip_x(self):
        """ The x-coordinate of the source chip of the packet
        
        :return: The x-coordinate of the chip, between 0 and 255
        :rtype: int
        """
        return self._source_chip_x
    
    @source_chip_x.setter
    def source_chip_x(self, source_chip_x):
        """ Set the x-coordinate of the source chip of the packet
        
        :param source_chip_x: The x-coordinate to set, between 0 and 255
        :type source_chip_x: int
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If the\
                    source_chip_x has already been set or if the value is out\
                    of range
        """
        if self._source_chip_x is not None:
            raise SpinnmanInvalidParameterException(
                    "source_chip_x", str(source_chip_x), "Already set")
        if source_chip_x is not None and (source_chip_x < 0 
                or source_chip_x > 255):
            raise SpinnmanInvalidParameterException(
                    "source_chip_x", str(source_chip_x), 
                    "Must be between 0 and 255")
            
        self._source_chip_x = source_chip_x
    
    @property  
    def source_chip_y(self):
        """ The y-coordinate of the source chip of the packet
        
        :return: The y-coordinate of the chip, between 0 and 255
        :rtype: int
        """
        return self._source_chip_y
    
    @source_chip_y.setter
    def source_chip_y(self, source_chip_y):
        """ Set the y-coordinate of the source chip of the packet
        
        :param source_chip_y: The y-coordinate to set, between 0 and 255
        :type source_chip_y: int
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If the\
                    source_chip_y has already been set or if the value is out\
                    of range
        """
        if self._source_chip_y is not None:
            raise SpinnmanInvalidParameterException(
                    "source_chip_y", str(source_chip_y), "Already set")
        if source_chip_y is not None and (source_chip_y < 0 
                or source_chip_y > 255):
            raise SpinnmanInvalidParameterException(
                    "source_chip_y", str(source_chip_y), 
                    "Must be between 0 and 255")
            
        self._source_chip_y = source_chip_y
    
    @property
    def source_cpu(self):
        """ The core on the source chip
        
        :return: The core on the source chip, between 0 and 31
        :rtype: int 
        """
        return self._source_cpu
    
    @source_cpu.setter
    def source_cpu(self, source_cpu):
        """ Set the id of the source processor of the packet
        
        :param source_cpu: The y-coordinate to set, between 0 and 31
        :type source_cpu: int
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If the\
                    source_cpu has already been set or if the value is out\
                    of range
        """
        if self._source_cpu is not None:
            raise SpinnmanInvalidParameterException(
                    "source_cpu", str(source_cpu), "Already set")
        if source_cpu is not None and (source_cpu < 0 
                or source_cpu > 31):
            raise SpinnmanInvalidParameterException(
                    "source_cpu", str(source_cpu), 
                    "Must be between 0 and 31")
            
        self._source_cpu = source_cpu
    
    @property
    def data(self):
        """ The data in the packet
        
        :return: The data
        :rtype: bytearray
        """
        return self._data
