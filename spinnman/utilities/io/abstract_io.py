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
from abc import (ABCMeta, abstractmethod, abstractproperty)
from six import add_metaclass
from spinnman.processes.fill_process import FillDataType


@add_metaclass(ABCMeta)
class AbstractIO(object):
    __slots__ = []

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

    @abstractmethod
    def fill(
            self, repeat_value, bytes_to_fill=None,
            data_type=FillDataType.WORD):
        """ Fill the next part of the region with repeated data

        :param repeat_value: The value to repeat
        :type repeat_value: int
        :param bytes_to_fill:\
            Optional number of bytes to fill from current position, or None\
            to fill to the end
        :type bytes_to_fill: int
        :param data_type: The type of the repeat value
        :type data_type: :py:class:`spinnman.process.fill_process.FillDataType`
        :raise EOFError: If the amount of data to fill is more than the region
        """
