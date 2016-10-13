import os
from spinnman.utilities.io.abstract_io import AbstractIO


class FileIO(AbstractIO):
    """ A file input/output interface to match the MemoryIO interface
    """

    __slots__ = [

        # The file to write to
        "_file",

        # The total size of the file
        "_size",

        # The maximum position seen in the file
        "_max_position",

        # The start offset in the file
        "_start_offset",

        # The end offset in the file
        "_end_offset"
    ]

    def __init__(
            self, file_obj, start_offset, end_offset):
        """

        :param file_obj: The file handle or file name to write to
        :type file_obj: str or file
        :param start_offset: The start offset into the file
        :type start_offset: int
        :param end_offset: The end offset from the start of the file
        :type end_offset: int or None
        """
        self._file = file_obj
        if isinstance(file_obj, str):
            self._file = open(file_obj, "wb+")
        self._file.seek(start_offset)

        self._start_offset = start_offset
        self._end_offset = end_offset

    def __len__(self):
        """ The size of the entire region of memory
        """
        return self._end_offset - self._start_offset

    def __getitem__(self, new_slice):
        """ Get a sub-region of this file object.  The index or slice must\
            be in range of the current region to be valid.

        :param new_slice:\
            A single index for a single byte, or a contiguous slice
        :rtype: :py:class:`~FileIO`
        :raise ValueError:\
            If the index or slice is outside of the current region
        """
        if isinstance(new_slice, int):
            if new_slice >= len(self):
                raise ValueError("Index {} out of range".format)
            return FileIO(
                self._file, self._start_offset + new_slice,
                self._start_offset + new_slice + 1)
        elif isinstance(new_slice, slice):
            if new_slice.step is not None and new_slice.step != 1:
                raise ValueError("Slice must be contiguous")
            start_offset = self._start_offset
            end_offset = self._end_offset
            if new_slice.start is not None:
                if new_slice.start < 0:
                    start_offset = self._end_offset + new_slice.start
                else:
                    start_offset = self._start_offset + new_slice.start
            if new_slice.stop is not None:
                if new_slice.stop > 0:
                    end_offset = self._start_offset + new_slice.stop
                else:
                    end_offset = self._end_offset + new_slice.stop

            if (start_offset < self._start_offset or
                    end_offset < self._start_offset or
                    end_offset > self._end_offset or
                    start_offset > self._end_offset):
                raise ValueError("Slice {} outside of this region".format(
                    new_slice))
            if start_offset == end_offset:
                raise ValueError("Zero sized regions are not supported")

            return FileIO(self._file, start_offset, end_offset)

    def __enter__(self):
        """ Enter a new block which will call :py:meth:`~.close` when exited.
        """
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        """ Exit a block and call :py:meth:`~.close`.
        """
        self.close()

    def close(self):
        """ Close the IO object
        """
        self._file.close()

    @property
    def closed(self):
        return self._file.closed

    def flush(self):
        """ Flush any outstanding written data
        """
        self._file.flush()

    def seek(self, n_bytes, from_what=os.SEEK_SET):
        """ Seek to a position within the region
        """
        position = 0
        if from_what == os.SEEK_SET:
            position = self._start_offset + n_bytes
        elif from_what == os.SEEK_CUR:
            position = self._file.tell() + n_bytes
        elif from_what == os.SEEK_END:
            position = self._end_offset + n_bytes
        else:
            raise ValueError(
                "Value of from_what must be one of os.SEEK_SET, os.SEEK_CUR"
                " or os.SEEK_END")

        if position < self._start_offset or position > self._end_offset:
            raise ValueError(
                "Attempt to seek to a position of {} which is outside of the"
                " region".format(position))

        self._file.seek(position)

    def tell(self):
        """ Return the current position within the region relative to the start
        """
        return self._file.tell() - self._start_offset

    @property
    def address(self):
        """ Return the current absolute address within the region
        """
        return self._file.tell()

    def read(self, n_bytes=None):
        """ Read a number of bytes, or the rest of the data if n_bytes is None\
            or negative

        :param n_bytes: The number of bytes to read
        :rtype: bytes
        :raise EOFError: If the read will be beyond the end of the region
        """
        if n_bytes == 0:
            return b""
        if n_bytes is None or n_bytes < 0:
            return self._file.read(self._end_offset - self._file.tell())
        return bytes(self._file.read(n_bytes))

    def write(self, data):
        """ Write some data to the region

        :param data: The data to write
        :type data: bytes
        :return: The number of bytes written
        :rtype: int
        :raise EOFError: If the write will go over the end of the region
        """
        n_bytes = len(data)
        if self._file.tell() + n_bytes > self._end_offset:
            raise EOFError

        self._file.write(data)
        return n_bytes
