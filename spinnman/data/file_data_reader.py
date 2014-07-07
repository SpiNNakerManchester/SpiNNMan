from spinnman.data.abstract_data_reader import AbstractDataReader

class FileDataReader(AbstractDataReader):
    """ A reader that can read data from a file
    """
    
    def __init__(self, filename):
        """
        :param filename: The file to read
        :type filename: str
        :raise spinnman.exceptions.SpinnmanIOException: If the file\
                    cannot found or opened for reading
        """
        pass
    
    def read(self, n_bytes):
        """ See :py:meth:`spinnman.data.abstract_data_reader.AbstractDataReader.read`
        """
        # TODO
        return None
    
    def readinto(self, data, offset=0, length=None):
        """ See :py:meth:`spinnman.data.abstract_data_reader.AbstractDataReader.readinto`
        """
        # TODO
        return 0
    
    def close(self):
        """ Closes the file
        
        :return: Nothing is returned:
        :rtype: None
        :raise spinnman.exceptions.SpinnmanIOException: If the file\
                    cannot be closed
        """
        # TODO
        pass
