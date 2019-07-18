# Copyright (c) 2017-2019 The University of Manchester
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import struct
from spinn_utilities.overrides import overrides
from spinnman.utilities.io.abstract_io import AbstractIO
from spinnman.processes.fill_process import FillDataType


class FileIO(AbstractIO):
    """ A file input/output interface to match the MemoryIO interface
    """

    __slots__ = [

        # The file to write to
        "_file",

        # The current offset in the file
        "_current_offset",

        # The start offset in the file
        "_start_offset",

        # The end offset in the file
        "_end_offset"
    ]

    def __init__(self, file_obj, start_offset, end_offset):
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

        self._current_offset = start_offset
        self._start_offset = start_offset
        self._end_offset = end_offset

    @overrides(AbstractIO.__len__)
    def __len__(self):
        return self._end_offset - self._start_offset

    @overrides(AbstractIO.__getitem__)
    def __getitem__(self, new_slice):
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

    @overrides(AbstractIO.__enter__)
    def __enter__(self):
        return self

    @overrides(AbstractIO.__exit__)
    def __exit__(self, exception_type, exception_value, traceback):
        self.close()

    @overrides(AbstractIO.close)
    def close(self):
        self._file.close()

    @property
    @overrides(AbstractIO.closed)
    def closed(self):
        return self._file.closed

    @overrides(AbstractIO.flush)
    def flush(self):
        self._file.flush()

    @overrides(AbstractIO.seek)
    def seek(self, n_bytes, from_what=os.SEEK_SET):
        position = 0
        if from_what == os.SEEK_SET:
            position = self._start_offset + n_bytes
        elif from_what == os.SEEK_CUR:
            position = self._current_offset + n_bytes
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

        self._current_offset = position

    @overrides(AbstractIO.tell)
    def tell(self):
        return self._current_offset - self._start_offset

    @property
    @overrides(AbstractIO.address)
    def address(self):
        return self._current_offset

    @overrides(AbstractIO.read)
    def read(self, n_bytes=None):
        if n_bytes == 0:
            return b""
        if n_bytes is None or n_bytes < 0:
            n_bytes = self._end_offset - self._current_offset
        if self._current_offset + n_bytes > self._end_offset:
            raise EOFError

        self._file.seek(self._current_offset)
        data = bytes(self._file.read(n_bytes))
        self._current_offset += n_bytes
        return data

    @overrides(AbstractIO.write)
    def write(self, data):
        n_bytes = len(data)

        if self._current_offset + n_bytes > self._end_offset:
            raise EOFError

        self._file.seek(self._current_offset)
        self._file.write(data)
        self._current_offset += n_bytes
        return n_bytes

    @overrides(AbstractIO.fill)
    def fill(self, repeat_value, bytes_to_fill=None,
             data_type=FillDataType.WORD):
        if bytes_to_fill is None:
            bytes_to_fill = self._end_offset - self._current_offset
        if self._current_offset + bytes_to_fill > self._end_offset:
            raise EOFError
        if bytes_to_fill % data_type.value != 0:
            raise ValueError(
                "The size of {} bytes to fill is not divisible by the size of"
                " the data of {} bytes".format(bytes_to_fill, data_type.value))
        data_to_fill = struct.pack(
            str(data_type.struct_type[-1]), repeat_value
        )
        self._file.seek(self._current_offset)
        for _ in range(bytes_to_fill // data_type.value):
            self._file.write(data_to_fill)
        self._current_offset += bytes_to_fill
