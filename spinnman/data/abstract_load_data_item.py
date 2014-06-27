from abc import ABCMeta
from abc import abstractmethod
from six import add_metaclass

from spinnman.data.abstract_executable_data_item import AbstractExecutableDataItem

@add_metaclass(ABCMeta)
class AbstractLoadDataItem(AbstractExecutableDataItem):
    """ An abstract representation of an item that can be loaded in to spinnaker
    """
    
    @abstractmethod
    def get_base_address(self):
        """ Return the base address at which the data should be loaded
        
        :return: The base address where the data is to be loaded
        :rtype: int
        :raise spinnman.exceptions.SpinnmanIOException: If there is a problem\
                    reading the data
        """
        pass
