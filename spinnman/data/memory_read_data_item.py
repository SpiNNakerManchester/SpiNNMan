from spinnman.data.abstract_read_data_item import AbstractReadDataItem

class MemoryReadDataItem(AbstractReadDataItem):
    """ A Memory-based implementation of AbstractReadDataItem
    """
    
    def __init__(self, read_locations, base_address, length):
        """ 
        :param read_locations: An iterable of chips and cores\
                    indicating where the data is to be read from
        :type read_locations: iterable of\
                    spinnman.model.chips_and_cores.ChipsAndCores
        :param base_address: The base address from which to read the data
        :type base_address: int
        :param length: The amount of data to read
        :type length: int
        :raise None: No known exceptions are raised
        """
        pass
    
    def get_chips_and_cores(self):
        """ See :py:meth:`spinnman.data.abstract_read_data_item.AbstractReadDataItem.get_chips_and_cores`
        """
        pass
    
    def get_length(self):
        """ See :py:meth:`spinnman.data.abstract_read_data_item.AbstractReadDataItem.get_length`
        """
        pass
    
    def get_base_address(self):
        """ See :py:meth:`spinnman.data.abstract_read_data_item.AbstractReadDataItem.get_base_address`
        """
        pass
    
    def get_writer(self, x, y, p):
        """ See :py:meth:`spinnman.data.abstract_read_data_item.AbstractReadDataItem.get_writer`
        """
        pass
