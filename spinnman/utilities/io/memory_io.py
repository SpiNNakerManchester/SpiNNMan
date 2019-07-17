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

# A set of ChipMemoryIO objects that have been created,
# indexed by transceiver, x and y (thus two transceivers might not see the
# same buffered memory)
_chip_memory_io_objects = dict()

# Start of SDRAM, using *unbuffered* memory access protocol.
UNBUFFERED_SDRAM_START = 0x60000000


def _get_chip_memory_io(transceiver, x, y):
    if (transceiver, x, y) not in _chip_memory_io_objects:
        _chip_memory_io_objects[transceiver, x, y] = _ChipMemoryIO(
            transceiver, x, y)
    return _chip_memory_io_objects[transceiver, x, y]


class _ChipMemoryIO(object):
    """ A file-like object for the memory of a chip
    """

    __slots__ = [

        # The transceiver for speaking to the machine
        "_transceiver",

        # The x coordinate of the chip to communicate with
        "_x",

        # The y coordinate of the chip to communicate with
        "_y",

        # The current pointer where read and writes are taking place
        "_current_address",

        # The current pointer where the next buffered write will occur
        "_write_address",

        # The write buffer size
        "_buffer_size",

        # The write buffer bytearray
        "_write_buffer",

        # The write buffer memory view
        "_write_memory_view",

        # The write buffer pointer
        "_write_buffer_offset"
    ]

    def __init__(
            self, transceiver, x, y, base_address=UNBUFFERED_SDRAM_START,
            buffer_size=256):
        """
        :param transceiver: The transceiver to read and write with
        :param x: The x-coordinate of the chip to write to
        :param y: The y-coordinate of the chip to write to
        :param base_address: The lowest address that can be written
        :param buffer_size: The size of the write buffer to improve efficiency
        """
        # pylint: disable=too-many-arguments
        self._transceiver = transceiver
        self._x = x
        self._y = y
        self._current_address = base_address
        self._write_address = base_address
        self._buffer_size = buffer_size
        self._write_buffer = bytearray(self._buffer_size)
        self._write_memory_view = memoryview(self._write_buffer)
        self._write_buffer_offset = 0

    @property
    def transceiver(self):
        return self._transceiver

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    def flush_write_buffer(self):
        """ Force the writing of the current write buffer
        """
        if self._write_buffer_offset > 0:
            self._transceiver.write_memory(
                self._x, self._y, self._write_address, self._write_buffer,
                n_bytes=self._write_buffer_offset)
            self._write_address += self._write_buffer_offset
            self._write_buffer_offset = 0

    @property
    def current_address(self):
        """ Return the current absolute address within the region
        """
        return self._current_address

    @current_address.setter
    def current_address(self, address):
        """ Seek to a position within the region
        """
        self.flush_write_buffer()
        self._current_address = address
        self._write_address = address

    def read(self, n_bytes):
        """ Read a number of bytes

        :param n_bytes: The number of bytes to read
        :rtype: bytes
        """
        if n_bytes == 0:
            return b""

        self.flush_write_buffer()
        data = self._transceiver.read_memory(
            self._x, self._y, self._current_address, n_bytes)
        self._current_address += n_bytes
        self._write_address = self._current_address

        return data

    def write(self, data):
        """ Write some data

        :param data: The data to write
        :type data: bytes
        """
        n_bytes = len(data)

        if n_bytes >= self._buffer_size:
            self.flush_write_buffer()
            self._transceiver.write_memory(
                self._x, self._y, self._current_address, data)
            self._current_address += n_bytes
            self._write_address = self._current_address

        else:
            n_bytes_to_copy = min(
                n_bytes, self._buffer_size - self._write_buffer_offset)
            self._write_memory_view[
                self._write_buffer_offset:
                self._write_buffer_offset + n_bytes_to_copy
            ] = data[:n_bytes_to_copy]
            self._write_buffer_offset += n_bytes_to_copy
            self._current_address += n_bytes_to_copy
            n_bytes -= n_bytes_to_copy
            if self._write_buffer_offset == self._buffer_size:
                self.flush_write_buffer()
            if n_bytes > 0:
                self._write_memory_view[:n_bytes] = data[n_bytes_to_copy:]
                self._write_buffer_offset += n_bytes
                self._current_address += n_bytes

    def fill(self, repeat_value, bytes_to_fill, data_type=FillDataType.WORD):
        """ Fill the memory with repeated data

        :param repeat_value: The value to repeat
        :type repeat_value: int
        :param bytes_to_fill: Number of bytes to fill from current position
        :type bytes_to_fill: int
        :param data_type: The type of the repeat value
        :type data_type: \
            :py:class:`spinnman.processes.fill_process.FillDataType`
        """
        self.flush_write_buffer()
        self._transceiver.fill_memory(
            self._x, self._y, self._current_address, repeat_value,
            bytes_to_fill, data_type)
        self._current_address += bytes_to_fill


class MemoryIO(AbstractIO):
    """ A file-like object for reading and writing memory
    """

    __slots__ = [

        # The transceiver for speaking to the machine
        "_chip_memory_io",

        # The start address of the region to write to
        "_start_address",

        # The current pointer where read and writes are taking place
        "_current_address",

        # The end of the region to write to
        "_end_address"
    ]

    # Cache of all writes that are currently buffered in any instance, to
    # ensure they are written before a read occurs
    __write_cache__ = dict()

    def __init__(self, transceiver, x, y, start_address, end_address):
        """
        :param transceiver: The transceiver to read and write with
        :param x: The x-coordinate of the chip to write to
        :param y: The y-coordinate of the chip to write to
        :param start_address: The start address of the region to write to
        :param end_address:\
            The end address of the region to write to.  This is the first\
            address just outside the region
        """
        # pylint: disable=too-many-arguments
        if start_address >= end_address:
            raise ValueError("Start address must be less than end address")

        self._chip_memory_io = _get_chip_memory_io(transceiver, x, y)
        self._start_address = start_address
        self._current_address = start_address
        self._end_address = end_address

    @overrides(AbstractIO.__len__)
    def __len__(self):
        return self._end_address - self._start_address

    @overrides(AbstractIO.__getitem__)
    def __getitem__(self, new_slice):
        if isinstance(new_slice, int):
            if new_slice >= len(self):
                raise ValueError("Index {} out of range".format)
            return MemoryIO(
                self._chip_memory_io.transceiver, self._chip_memory_io.x,
                self._chip_memory_io.y,
                self._start_address + new_slice,
                self._start_address + new_slice + 1)
        elif isinstance(new_slice, slice):
            if new_slice.step is not None and new_slice.step != 1:
                raise ValueError("Slice must be contiguous")
            start_address = self._start_address
            end_address = self._end_address
            if new_slice.start is not None:
                if new_slice.start < 0:
                    start_address = self._end_address + new_slice.start
                else:
                    start_address = self._start_address + new_slice.start
            if new_slice.stop is not None:
                if new_slice.stop > 0:
                    end_address = self._start_address + new_slice.stop
                else:
                    end_address = self._end_address + new_slice.stop

            if (start_address < self._start_address or
                    end_address < self._start_address or
                    end_address > self._end_address or
                    start_address > self._end_address):
                raise ValueError("Slice {} outside of this region".format(
                    new_slice))
            if start_address == end_address:
                raise ValueError("Zero sized regions are not supported")

            return MemoryIO(
                self._chip_memory_io.transceiver, self._chip_memory_io.x,
                self._chip_memory_io.y,
                start_address, end_address)

    @overrides(AbstractIO.__enter__)
    def __enter__(self):
        return self

    @overrides(AbstractIO.__exit__)
    def __exit__(self, exception_type, exception_value, traceback):
        self.close()
        return False

    @overrides(AbstractIO.close)
    def close(self):
        self._chip_memory_io.flush_write_buffer()

    @property
    @overrides(AbstractIO.closed)
    def closed(self):
        return False

    @overrides(AbstractIO.flush)
    def flush(self):
        self._chip_memory_io.flush_write_buffer()

    @overrides(AbstractIO.seek)
    def seek(self, n_bytes, from_what=os.SEEK_SET):
        """ Seek to a position within the region
        """
        position = 0
        if from_what == os.SEEK_SET:
            position = self._start_address + n_bytes
        elif from_what == os.SEEK_CUR:
            position = self._current_address + n_bytes
        elif from_what == os.SEEK_END:
            position = self._end_address + n_bytes
        else:
            raise ValueError(
                "Value of from_what must be one of os.SEEK_SET, os.SEEK_CUR"
                " or os.SEEK_END")

        if position < self._start_address or position > self._end_address:
            raise ValueError(
                "Attempt to seek to a position of {} which is outside of the"
                " region".format(position))

        self._current_address = position

    @overrides(AbstractIO.tell)
    def tell(self):
        return self._current_address - self._start_address

    @property
    def address(self):
        """ Return the current absolute address within the region
        """
        return self._current_address

    @overrides(AbstractIO.read)
    def read(self, n_bytes=None):
        bytes_to_read = n_bytes
        if n_bytes is None or n_bytes < 0:
            bytes_to_read = self._end_address - self._current_address

        if self._current_address + bytes_to_read > self._end_address:
            raise EOFError

        self._chip_memory_io.current_address = self._current_address
        data = bytes(self._chip_memory_io.read(bytes_to_read))
        self._current_address += bytes_to_read

        return data

    @overrides(AbstractIO.write)
    def write(self, data):
        n_bytes = len(data)

        if self._current_address + n_bytes > self._end_address:
            raise EOFError

        self._chip_memory_io.current_address = self._current_address
        self._chip_memory_io.write(data)
        self._current_address += n_bytes

        return n_bytes

    @overrides(AbstractIO.fill)
    def fill(self, repeat_value, bytes_to_fill=None,
             data_type=FillDataType.WORD):
        if bytes_to_fill is None:
            bytes_to_fill = self._end_address - self._current_address
        if self._current_address + bytes_to_fill > self._end_address:
            raise EOFError

        if bytes_to_fill % data_type.value != 0:
            raise ValueError(
                "The size of {} bytes to fill is not divisible by the size of"
                " the data of {} bytes".format(bytes_to_fill, data_type.value))
        data_to_fill = struct.pack(
            "{}".format(data_type.struct_type[-1]),
            repeat_value)
        self._chip_memory_io.current_address = self._current_address
        for _ in range(bytes_to_fill // data_type.value):
            self._chip_memory_io.write(data_to_fill)
        self._current_address += bytes_to_fill
