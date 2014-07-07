class VersionInfo(object):
    """ Decodes SC&MP/SARK version information as returned by the SVER command
    """

    def __init__(self, version_data):
        """
        :param version_data: bytes from an SCP packet containing version\
                    information
        :type version_data: bytearray
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If the\
                    message does not contain valid version information
        """
        pass
    
    @property
    def name(self):
        """ The name of the software
        
        :return: The name
        :rtype: str
        """
        pass
    
    @property
    def version_number(self):
        """ The version number of the software
        
        :return: The version
        :rtype: float
        """
        pass
    
    @property
    def hardware(self):
        """ The hardware being run on
        
        :return: The hardware
        :rtype: str
        """
        pass
    
    @property
    def x(self):
        """ The x-coordinate of the chip where the information was obtained
        
        :return: the x-coordinate
        :rtype: int
        """
        pass
    
    @property
    def y(self):
        """ The y-coordinate of the chip where the information was obtained
        
        :return: The y-coordinate
        :rtype: int
        """
        pass
    
    @property
    def p(self):
        """ The processor id of the processor where the information was obtained
        
        :return: the processor id
        :rtype: int
        """
        pass
    
    @property
    def build_date(self):
        """ The build date of the software
        
        :return: The number of seconds since 1st January 1970
        :rtype: long
        """
        pass
    
    @property
    def hardware_version(self):
        """ The version of the hardware being run on
        
        :return: The version
        :rtype: int
        """
        pass
    
    @property
    def version_string(self):
        """ The version information as text
        
        :return: The version information
        :rtype: str
        """
        pass
