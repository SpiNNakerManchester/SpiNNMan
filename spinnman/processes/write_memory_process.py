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

import functools
from spinnman.messages.scp.impl import WriteLink, WriteMemory
from .abstract_multi_connection_process import AbstractMultiConnectionProcess
from spinnman.constants import UDP_MESSAGE_MAX_SIZE


class WriteMemoryProcess(AbstractMultiConnectionProcess):
    """ A process for writing memory on a SpiNNaker chip.
    """
    __slots__ = []
    # pylint: disable=too-many-arguments

    def write_memory_from_bytearray(
            self, x, y, p, base_address, data, offset, n_bytes):
        """ Writes memory onto a SpiNNaker chip from a bytearray.

        :param x: \
            The x-coordinate of the chip where the memory is to be written to
        :param y: \
            The y-coordinate of the chip where the memory is to be written to
        :param p: \
            The processor of the chip where the memory is to be written to
        :param processor_address: the (x, y, p) coords of the chip in question
        :param base_address: the address in SDRAM to start writing
        :param data: the data to write
        :type data: bytearray or bytes
        :param offset: where in the data to start writing from
        :param n_bytes: how much data to write
        :rtype: None
        """
        self._write_memory_from_bytearray(
            base_address, data, offset, n_bytes,
            functools.partial(WriteMemory, x=x, y=y, cpu=p))

    def write_link_memory_from_bytearray(
            self, x, y, p, link, base_address, data, offset, n_bytes):
        self._write_memory_from_bytearray(
            base_address, data, offset, n_bytes,
            functools.partial(WriteLink, x=x, y=y, cpu=p, link=link))

    def write_memory_from_reader(
            self, x, y, p, base_address, reader, n_bytes):
        """ Writes memory onto a SpiNNaker chip from a reader.

        :param x: \
            The x-coordinate of the chip where the memory is to be written to
        :param y: \
            The y-coordinate of the chip where the memory is to be written to
        :param p: \
            The processor of the chip where the memory is to be written to
        :param base_address: the address in SDRAM to start writing
        :param reader: the readable object containing the data to write
        :type reader: :py:class:`io.RawIOBase` or :py:class:`io.BufferedIOBase`
        :param n_bytes: how much data to write
        :rtype: None
        """
        self._write_memory_from_reader(
            base_address, reader, n_bytes,
            functools.partial(WriteMemory, x=x, y=y, cpu=p))

    def write_link_memory_from_reader(
            self, x, y, p, link, base_address, reader, n_bytes):
        self._write_memory_from_reader(
            base_address, reader, n_bytes,
            functools.partial(WriteLink, x=x, y=y, cpu=p, link=link))

    def _write_memory_from_bytearray(
            self, base_address, data, data_offset, n_bytes, packet_class):
        offset = 0
        n_bytes_to_write = int(n_bytes)
        while n_bytes_to_write > 0:
            bytes_to_send = min((n_bytes_to_write, UDP_MESSAGE_MAX_SIZE))
            data_array = data[data_offset:data_offset + bytes_to_send]

            self._send_request(packet_class(
                base_address=base_address + offset, data=data_array))

            n_bytes_to_write -= bytes_to_send
            offset += bytes_to_send
            data_offset += bytes_to_send
        self._finish()
        self.check_for_error()

    def _write_memory_from_reader(
            self, base_address, reader, n_bytes, packet_class):
        offset = 0
        n_bytes_to_write = int(n_bytes)
        while n_bytes_to_write > 0:
            data_array = reader.read(
                min((n_bytes_to_write, UDP_MESSAGE_MAX_SIZE)))
            bytes_to_send = len(data_array)

            self._send_request(packet_class(
                base_address=base_address + offset, data=data_array))

            n_bytes_to_write -= bytes_to_send
            offset += bytes_to_send
        self._finish()
        self.check_for_error()
