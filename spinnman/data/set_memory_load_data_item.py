from spinnman.data.abstract_load_data_item import AbstractLoadDataItem

class SetMemoryDataItem(AbstractLoadDataItem):
    """ An implementation of AbstractLoadDataItem that sets a single word value\
        at a single memory address
    """
    
    def __init__(self, x, y, p, address, value):
        """
        :param x: The x-coordinate of the chip
        :type x: int
        :param y: The y-coordinate of the chip
        :type y: int
        :param p: The core on the chip
        :type p: int
        :param address: The address where the value is to be set
        :type address: int
        :param value: The value to write
        :type value: int
        :raise None: No known exceptions are raised
        """
        pass
    
    def get_chips_and_cores(self):
        """ See :py:meth:`spinnman.abstract_executable_data_item.AbstractExecutableDataItem.get_chips`
        """
        # TODO
        return None
    
    def get_n_chunks(self, chunk_size):
        """ See :py:meth:`spinnman.abstract_executable_data_item.AbstractExecutableDataItem.get_n_chunks`
        """
        # TODO
        return 0
    
    def get_chunks(self, chunk_size):
        """ See :py:meth:`spinnman.abstract_executable_data_item.AbstractExecutableDataItem.get_chunks`
        """
        # TODO
        return None
    
    def get_base_address(self):
        """ See :py:meth:`spinnman.abstract_load_data_item.AbstractLoadDataItem.get_base_address`
        """
        # TODO
        return 0
