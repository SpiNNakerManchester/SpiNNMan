from six import add_metaclass
from abc import ABCMeta
import os
from abc import abstractmethod
from abc import abstractproperty


@add_metaclass(ABCMeta)
class AbstractIO(object):

    @abstractmethod
    def __len__(self):
        """ The size of the entire region of memory
        """

    @abstractmethod
    def __getitem__(self, new_slice):
        """ Get a sub-region of this memory object.  The index or slice must\
            be in range of the current region to be valid.

        :param new_slice:\
            A single index for a single byte of memory, or a contiguous slice
        :rtype: :py:class:`~MemoryIO`
        :raise ValueError:\
            If the index or slice is outside of the current region
        """

    @abstractmethod
    def __enter__(self):
        """ Enter a new block which will call :py:meth:`~.close` when exited.
        """

    @abstractmethod
    def __exit__(self, exception_type, exception_value, traceback):
        """ Exit a block and call :py:meth:`~.close`.
        """

    @abstractmethod
    def close(self):
        """ Close the IO object
        """

    @abstractproperty
    def closed(self):
        """ Indicates if the object has been closed
        """

    @abstractmethod
    def flush(self):
        """ Flush any outstanding written data
        """

    @abstractmethod
    def seek(self, n_bytes, from_what=os.SEEK_SET):
        """ Seek to a position within the region
        """

    @abstractmethod
    def tell(self):
        """ Return the current position within the region relative to the start
        """
        return self._current_address - self._start_address

    @abstractproperty
    def address(self):
        """ Return the current absolute address within the region
        """

    @abstractmethod
    def read(self, n_bytes=None):
        """ Read a number of bytes, or the rest of the data if n_bytes is None\
            or negative

        :param n_bytes: The number of bytes to read
        :rtype: bytes
        :raise EOFError: If the read will be beyond the end of the region
        """

    @abstractmethod
    def write(self, data):
        """ Write some data to the region

        :param data: The data to write
        :type data: bytes
        :return: The number of bytes written
        :rtype: int
        :raise EOFError: If the write will go over the end of the region
        """
