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

import logging
import struct
from enum import Enum
from spinnman.messages.scp.impl import FillRequest, WriteMemory
from spinnman.processes.abstract_multi_connection_process import (
    AbstractMultiConnectionProcess)

logger = logging.getLogger(__name__)
ALIGNMENT = 4


class FillDataType(Enum):

    WORD = (4, "<I")
    HALF_WORD = (2, "<2H")
    BYTE = (1, "<4B")

    def __new__(cls, value, struct_type, doc=""):
        # pylint: disable=protected-access, unused-argument
        obj = object.__new__(cls)
        obj._value_ = value
        obj._struct_type = struct_type
        obj._struct = struct.Struct(struct_type)
        return obj

    def __init__(self, value, struct_type, doc=""):
        self._value_ = value
        self._struct_type = struct_type
        self._struct = struct.Struct(struct_type)
        self.__doc__ = doc

    @property
    def struct_type(self):
        """ The struct descriptor for packing and unpacking 4 bytes-worth of\
            this type.

        :rtype: str
        """
        return self._struct_type

    @property
    def struct(self):
        """ An object that can pack and unpack 4 bytes-worth of this type.

        :rtype: struct.Struct
        """
        return self._struct


class FillProcess(AbstractMultiConnectionProcess):
    """ A process for filling memory.
    """
    __slots__ = []

    _PACKS = [struct.Struct("<{}B".format(i)) for i in range(ALIGNMENT)]

    # pylint: disable=too-many-arguments

    def _write_pre_bytes(self, x, y, base, data_to_fill, size):
        extra_bytes = (ALIGNMENT - base % ALIGNMENT) % ALIGNMENT
        if not extra_bytes:
            return 0
        # Pre_bytes is the first part of the data up to the first aligned
        # word
        pre_bytes = self._PACKS[extra_bytes].pack(*data_to_fill[:extra_bytes])
        # Send the pre-data to make the memory aligned (or all the
        # data if the size is correct - note that pre_bytes[:size] will
        # return all of pre_bytes if size >= len(pre_bytes)
        pre_data = pre_bytes[:size]
        if not pre_data:
            return 0
        self._send_request(WriteMemory(x, y, base, pre_data))
        return extra_bytes

    def _write_fill(self, x, y, address, base, data_to_fill, size):
        extra_bytes = (ALIGNMENT - base % ALIGNMENT) % ALIGNMENT
        size = size - ALIGNMENT if extra_bytes else size
        if not size:
            return 0
        # The data to send is the repeated fill data, from the end of the
        # pre-data circling round to the start of the post-data; we double
        # it up so that we don't need to use mod (it's pretty small).
        data = data_to_fill + data_to_fill
        fill_word = FillDataType.WORD.struct.unpack(
            data[extra_bytes:extra_bytes + ALIGNMENT - 1])[0]
        self._send_request(FillRequest(x, y, address, fill_word, size))
        return size

    def _write_post_bytes(
            self, x, y, address, base, data_to_fill, bytes_to_write):
        # Post bytes is the last part of the data from the end of the last
        # aligned word; the number of bytes to write here is exactly the
        # number of bytes later than a word boundary the initial address is.
        n_bytes = base % ALIGNMENT
        if not n_bytes or not bytes_to_write:
            return

        post_bytes = self._PACKS[n_bytes].pack(*data_to_fill[-n_bytes:])
        self._send_request(WriteMemory(
            x, y, address, post_bytes[:bytes_to_write]))

    def fill_memory(self, x, y, base_address, data, size, data_type):
        """
        :type x: int
        :type y: int
        :type base_address: int
        :type data: int
        :type size: int
        :type data_type: spinnman.processes.fill_process.FillDataType
        """
        # Don't do anything if there is nothing to do!
        if size == 0:
            return

        # Check that the data can fill the requested size
        if size % data_type.value:
            raise Exception(
                "The size of {} bytes to fill is not divisible by the size of"
                " the data of {} bytes".format(size, data_type.value))
        if base_address % ALIGNMENT:
            logger.warning(
                "Unaligned fill starting at %d; please use aligned fills",
                base_address)

        # Get a word of data regardless of the type
        data_to_fill = bytearray(data_type.struct.pack(
            *([data] * (ALIGNMENT / data_type.value))))

        written = 0
        address = base_address

        # Send the pre-data to make the memory aligned (or all the
        # data if the size is correct - note that pre_bytes[:size] will
        # return all of pre_bytes if size >= len(pre_bytes)
        delta = self._write_pre_bytes(x, y, base_address, data_to_fill, size)
        written += delta
        address += delta

        # Fill as much as possible
        delta = self._write_fill(
            x, y, address, base_address, data_to_fill, size)
        written += delta
        address += delta

        # Post bytes is the last part of the data from the end of the last
        # aligned word; send them if required
        self._write_post_bytes(
            x, y, address, base_address, data_to_fill, size - written)

        # Wait for all the packets to be confirmed and then check there
        # are no errors
        self._finish()
        self.check_for_error()
