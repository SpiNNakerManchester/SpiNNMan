from spinnman.data.abstract_data_reader import AbstractDataReader
from io import FileIO
from spinnman.exceptions import SpinnmanIOException


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
        try:
            self._fileio = FileIO(filename, "r")
        except IOError as e:
            raise SpinnmanIOException(str(e))

    def read(self, n_bytes):
        """ See :py:meth:`spinnman.data.abstract_data_reader.AbstractDataReader.read`
        """
        return bytearray(self._fileio.read(n_bytes))

    def readinto(self, data):
        """ See :py:meth:`spinnman.data.abstract_data_reader.AbstractDataReader.readinto`
        """
        return self._fileio.readinto(data)

    def readall(self):
        """ See :py:meth:`spinnman.data.abstract_data_reader.AbstractDataReader.readall`
        """
        return self._fileio.readall()

    def close(self):
        """ Closes the file

        :return: Nothing is returned:
        :rtype: None
        :raise spinnman.exceptions.SpinnmanIOException: If the file\
                    cannot be closed
        """
        try:
            self._fileio.close()
        except IOError as e:
            raise SpinnmanIOException(str(e))
