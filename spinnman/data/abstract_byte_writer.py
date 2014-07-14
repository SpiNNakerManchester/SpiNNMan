from abc import ABCMeta
from abc import abstractmethod
from six import add_metaclass


@add_metaclass(ABCMeta)
class AbstractByteWriter(object):
    """ An abstract writer of bytes.  Note that due to endianness concerns,\
        the methods of this writer should be used directly for the appropriate\
        data type being written; e.g. an int should be written using write_int\
        rather than calling write_byte 4 times with the parts of the int\
        unless a specific endianness is being achieved.
    """
    
    @abstractmethod
    def write_byte(self, byte_value):
        """ Writes the lowest order byte of the given value
        
        :param byte_value: The byte to write
        :type byte_value: int
        :return: Nothing is returned
        :rtype: None
        :raise IOError: If there is an error writing to the stream
        """
        pass
    
    def write_bytes(self, byte_iterable):
        """ Writes a set of bytes
        
        :param bytes: The bytes to write
        :type bytes: iterable of bytes
        :return: Nothing is returned
        :rtype: None
        :raise IOError: If there is an error writing to the stream
        """
        pass
    
    @abstractmethod
    def write_short(self, short_value):
        """ Writes the two lowest order bytes of the given value
        
        :param short_value: The short to write
        :type short_value: int
        :return: Nothing is returned
        :rtype: None
        :raise IOError: If there is an error writing to the stream
        """
        pass
    
    @abstractmethod
    def write_int(self, int_value):
        """ Writes a four byte value
        
        :param int_value: The integer to write
        :type int_value: int
        :return: Nothing is returned
        :rtype: None
        :raise IOError: If there is an error writing to the stream
        """
        pass
    
    @abstractmethod
    def write_long(self, long_value):
        """ Writes an eight byte value
        
        :param long_value: The long to write
        :type long: long
        :return: Nothing is returned
        :rtype: None
        :raise IOError: If there is an error writing to the stream
        """
        pass
