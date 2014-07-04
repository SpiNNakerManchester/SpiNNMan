from abc import ABCMeta
from abc import abstractmethod
from six import add_metaclass

@add_metaclass(ABCMeta)
class AbstractReadDataItem(object):
    """ An abstract data item used to indicate where to read data from and\
        where to store it on the board
    """
    
    @abstractmethod
    def get_core_subsets(self):
        """ Return the chips and the cores on the chips where the data is to\
            be read from
        
        :return: The chips and cores
        :rtype: :py:class:`spinnman.model.core_subsets.CoreSubsets`
        :raise None: No known exceptions are raised
        """
        pass
    
    @abstractmethod
    def get_base_address(self):
        """ Return the base address from which to start reading memory
        
        :return: The base address in SDRAM from which reading should start
        :rtype: int
        :raise None: No known exceptions are raised
        """
        pass
    
    @abstractmethod
    def get_length(self):
        """ The amount of data to read
        
        :return: The amount of data to read in bytes
        :rtype: int
        :raise None: No known exceptions are raised
        """
        pass
    
    @abstractmethod
    def get_writer(self, x, y, p):
        """ Get a writer that will write the data read for a specific core
        
        :param x: The x-coordinate of the chip
        :type x: int
        :param y: The y-coordinate of the chip
        :type y: int
        :param p: The core on the chip
        :type p: int
        :return: A writer for the core
        :rtype: :py:class:`spinnman.data.abstract_read_data_writer.AbstractReadDataWriter`
        :raise: spinnman.execptions.SpinnmanIOException: If there is a problem\
                    obtaining the writer
        """
        pass
