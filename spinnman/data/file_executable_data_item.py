from spinnman.data.abstract_executable_data_item import AbstractExecutableDataItem

class FileExecutableDataItem(AbstractExecutableDataItem):
    """ An implementation of AbstractExecutableDataItem that reads data from\
        a file
    """
    
    def __init__(self, filename, load_locations):
        """
        :param filename: The name of the file containing the executable
        :type filename: str
        :param load_locations: An iterable of chips and cores\
                    indicating where the executable is to be loaded
        :type load_locations: iterable of\
                    spinnman.model.chips_and_cores.ChipsAndCores
        :raise spinnman.exceptions.SpinnmanIOException: If the file is\
                    cannot be read
        """
        
    def get_chips_and_cores(self):
        """ See :py:meth:`spinnman.data.abstract_executable_data_item.AbstractExecutableDataItem.get_chips_and_cores`
        """
        # TODO
        return None
    
    def get_n_chunks(self, chunk_size):
        """ See :py:meth:`spinnman.data.abstract_executable_data_item.AbstractExecutableDataItem.get_n_chunks`
        """
        # TODO
        return 0
    
    def get_chunks(self, chunk_size):
        """ See :py:meth:`spinnman.data.abstract_executable_data_item.AbstractExecutableDataItem.get_chunks`
        """
        # TODO
        return None
