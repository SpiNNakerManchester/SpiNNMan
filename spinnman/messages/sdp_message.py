from enum import Enum

class SDPMessage(object):
    """ Wraps up an SDP message.
    """
    
    class Flag(Enum):
        """ Flag for the message:
            
            ================== ===========================================
            Flag               Description
            ================== ===========================================
            REPLY_NOT_EXPECTED Indicates that a reply is not expected
            REPLY_EXCPECTED    Indicates that a reply is expected
            ================== ===========================================
        """
        REPLY_NOT_EXPECTED = 0x07
        REPLY_EXPECTED = 0x87

    def __init__(self, flags, tag, destination_port, destination_chip_x, 
            destination_chip_y, destination_cpu, source_port,
            source_chip_x, source_chip_y, source_cpu, data):
        """
        :param flags: Any flags for the packet
        :type flags: Flag
        :param tag: The ip tag of the packet between 0 and 255
        :type tag: int
        :param destination_port: The destination port of the packet between 1\
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
        :param source_port: The source port of the packet between 1 and 7
        :type source_port: int
        :param source_chip_x: The x-coordinate of the source chip\
                    between 0 and 255
        :type source_chip_x: int
        :param source_chip_y: The y-coordinate of the source chip\
                    between 0 and 255
        :param source_cpu: The source processor id within the chip\
                   between 0 and 31
        :type source_cpu: int
        :param data: The data of the SDP packet
        :type data: bytearray
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If one of\
                    the parameters is not valid
        """
        pass
    
    @property
    def flags(self):
        """ The flags of the packet
        
        :return: The flags of the packet
        :rtype: Flag
        """
        pass
    
    @property
    def tag(self):
        """ The tag of the packet
        
        :return: The tag of the packet between 0 and 255
        :rtype: int
        """
        pass
    
    @property
    def destination_port(self):
        """ The destination port of the packet
        
        :return: The destination port of the packet between 0 and 7
        :rtype: int
        """
        pass
        
    @property
    def destination_chip_x(self):
        """ The x-coordinate of the destination chip of the packet
        
        :return: The x-coordinate of the chip, between 0 and 255
        :rtype: int
        """
        pass
    
    @property  
    def destination_chip_y(self):
        """ The y-coordinate of the destination chip of the packet
        
        :return: The y-coordinate of the chip, between 0 and 255
        :rtype: int
        """
        pass
    
    @property
    def destination_cpu(self):
        """ The core on the destination chip
        
        :return: The core on the destination chip, between 0 and 31
        :rtype: int 
        """
        pass
    
    @property
    def source_port(self):
        """ The source port of the packet
        
        :return: The source port of the packet between 0 and 7
        :rtype: int
        """
        pass
        
    @property
    def source_chip_x(self):
        """ The x-coordinate of the source chip of the packet
        
        :return: The x-coordinate of the chip, between 0 and 255
        :rtype: int
        """
        pass
    
    @property  
    def source_chip_y(self):
        """ The y-coordinate of the source chip of the packet
        
        :return: The y-coordinate of the chip, between 0 and 255
        :rtype: int
        """
        pass
    
    @property
    def source_cpu(self):
        """ The core on the source chip
        
        :return: The core on the source chip, between 0 and 31
        :rtype: int 
        """
        pass
    
    @property
    def data(self):
        """ The data in the packet
        
        :return: The data
        :rtype: bytearray
        """
        pass
    