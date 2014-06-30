from spinnman.data.abstract_load_data_item import AbstractLoadDataItem
from spinnman.data.file_executable_data_item import FileExecutableDataItem

class FileLoadDataItem(AbstractLoadDataItem, FileExecutableDataItem):
    """ An implementation of AbstractLoadDataItem that loads data from a file
    """
    
    def __init__(self, filename, load_locations, base_address):
        """
        :param filename: The name of the file containing the data
        :type filename: str
        :param load_locations: An iterable of chips and cores\
                    indicating where the data is to be loaded
        :type load_locations: iterable of\
                    :py:class:`spinnman.model.chips_and_cores.ChipsAndCores`
        :param base_address: The base address at which to load the data
        :type base_address: int
        :raise spinnman.exceptions.SpinnmanIOException: If the file\
                    cannot be read
        """
        pass
    
    def get_base_address(self):
        """ See :py:meth:`spinnman.data.abstract_load_data_item.AbstractLoadDataItem.get_base_address`
        """
        # TODO
        return 0
