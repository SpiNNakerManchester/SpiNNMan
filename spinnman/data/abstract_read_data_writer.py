from abc import ABCMeta
from abc import abstractmethod
from six import add_metaclass

@add_metaclass(ABCMeta)
class AbstractReadDataWriter(object):
    """ An abstract writer of data that has been read from a memory location
    """
    
    @abstractmethod
    def write_bytes(self, data, offset=0, length=None):
        """ Write some bytes
    
        :param data: The data to be written
        :type data: bytearray
        :param offset: The offset into the array where the data to be written.\
                    If not specified, the offset is the start of the array
        :type offset: int
        :param length: The amount of data to write from the array, starting\
                    from the offset
        :type length: int
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    writing the data
        """
        pass
    
    def close(self):
        """ Indicates that all the data has finished being written
        
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    writing the data
        """
        pass
