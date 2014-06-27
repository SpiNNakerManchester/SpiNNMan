from abc import ABCMeta
from abc import abstractmethod
from six import add_metaclass

@add_metaclass(ABCMeta)
class AbstractExecutableDataItem(object):
    """ An abstract representation of an executable that can be loaded in to\
       spinnaker
    """
    
    @abstractmethod
    def get_chips_and_cores(self):
        """ Return the chips and the cores on the chips where the executable\
            is to be loaded
        
        :return: The chips and cores
        :rtype: spinnman.model.chips_and_cores.ChipsAndCores
        :raise spinnman.exceptions.SpinnmanIOException: If there is a problem\
                    reading the data
        """
        pass
    
    @abstractmethod
    def get_n_chunks(self, chunk_size):
        """ Return the number of chunks that will result with the given\
            chunk_size
        
        :param chunk_size: The size of the chunks in bytes
        :type chunk_size: int
        :return: The number of chunks
        :rtype: int
        :raise spinnman.exceptions.SpinnmanIOException: If there is a problem\
                    reading the data
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If the\
                    chunk_size is <= 0
        """
        pass
    
    @abstractmethod
    def get_chunks(self, chunk_size):
        """ Return an iterable of chunks of size <= chunk_size
        
        :param chunk_size: The size of the chunks in bytes
        :type chunk_size: int
        :return: An iterable of chunks
        :rtype: iterable of bytearray
        :raise spinnman.exceptions.SpinnmanIOException: If there is a problem\
                    reading the data
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If the\
                    chunk_size is <= 0
        """
        pass
