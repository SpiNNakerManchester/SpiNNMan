# Copyright (c) 2015 The University of Manchester
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import functools
from spinnman.messages.scp.impl import WriteLink, WriteMemory
from .abstract_multi_connection_process import AbstractMultiConnectionProcess
from spinnman.constants import UDP_MESSAGE_MAX_SIZE
import numpy


class WriteMemoryProcess(AbstractMultiConnectionProcess):
    """
    A process for writing memory on a SpiNNaker chip.
    """
    __slots__ = []
    # pylint: disable=too-many-arguments

    def write_memory_from_bytearray(
            self, x, y, p, base_address, data, offset, n_bytes,
            get_sum=False):
        """
        Writes memory onto a SpiNNaker chip from a bytearray.

        :param int x:
            The x-coordinate of the chip where the memory is to be written to
        :param int y:
            The y-coordinate of the chip where the memory is to be written to
        :param int p:
            The processor of the chip where the memory is to be written to
        :param int base_address: the address in SDRAM to start writing
        :param data: the data to write
        :type data: bytearray or bytes
        :param int offset: where in the data to start writing from
        :param int n_bytes: how much data to write
        :param bool get_sum: whether to return a checksum or 0
        :return: the data checksum or 0 if get_sum is False
        :rtype: int
        """
        return self._write_memory_from_bytearray(
            base_address, data, offset, n_bytes,
            functools.partial(WriteMemory, x=x, y=y, cpu=p), get_sum)

    def write_link_memory_from_bytearray(
            self, x, y, p, link, base_address, data, offset, n_bytes,
            get_sum=False):
        """
        Writes memory onto a neighbour of a SpiNNaker chip from a bytearray.

        :param int x:
            The x-coordinate of the chip where the memory is to be written to
        :param int y:
            The y-coordinate of the chip where the memory is to be written to
        :param int p:
            The processor of the chip where the memory is to be written to
        :param int link:
            Along which link is the neighbour.
        :param int base_address: the address in SDRAM to start writing
        :param data: the data to write
        :type data: bytearray or bytes
        :param int offset: where in the data to start writing from
        :param int n_bytes: how much data to write
        :param bool get_sum: whether to return a checksum or 0
        :return: the data checksum or 0 if get_sum is False
        :rtype: int
        """
        return self._write_memory_from_bytearray(
            base_address, data, offset, n_bytes,
            functools.partial(WriteLink, x=x, y=y, cpu=p, link=link), get_sum)

    def write_memory_from_reader(
            self, x, y, p, base_address, reader, n_bytes, get_sum=False):
        """
        Writes memory onto a SpiNNaker chip from a reader.

        :param int x:
            The x-coordinate of the chip where the memory is to be written to
        :param int y:
            The y-coordinate of the chip where the memory is to be written to
        :param int p:
            The processor of the chip where the memory is to be written to
        :param int base_address: the address in SDRAM to start writing
        :param reader: the readable object containing the data to write
        :type reader: ~io.RawIOBase or ~io.BufferedIOBase
        :param int n_bytes: how much data to write
        :param bool get_sum: whether to return a checksum or 0
        :return: the data checksum or 0 if get_sum is False
        :rtype: int
        """
        return self._write_memory_from_reader(
            base_address, reader, n_bytes,
            functools.partial(WriteMemory, x=x, y=y, cpu=p), get_sum)

    def write_link_memory_from_reader(
            self, x, y, p, link, base_address, reader, n_bytes,
            get_sum=False):
        """
        Writes memory onto a neighbour of a SpiNNaker chip from a reader.

        :param int x:
            The x-coordinate of the chip where the memory is to be written to
        :param int y:
            The y-coordinate of the chip where the memory is to be written to
        :param int p:
            The processor of the chip where the memory is to be written to
        :param int link:
            Along which link is the neighbour.
        :param int base_address: the address in SDRAM to start writing
        :param reader: the readable object containing the data to write
        :type reader: ~io.RawIOBase or ~io.BufferedIOBase
        :param int n_bytes: how much data to write
        :param bool get_sum: whether to return a checksum or 0
        :return: the data checksum or 0 if get_sum is False
        :rtype: int
        """
        return self._write_memory_from_reader(
            base_address, reader, n_bytes,
            functools.partial(WriteLink, x=x, y=y, cpu=p, link=link), get_sum)

    def _write_memory_from_bytearray(
            self, base_address, data, data_offset, n_bytes, packet_class,
            get_sum):
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
        if not get_sum:
            return 0
        np_data = numpy.array(data, dtype="uint8")
        np_sum = int(numpy.sum(np_data.view("uint32"), dtype="uint32"))
        return np_sum & 0xFFFFFFFF

    def _write_memory_from_reader(
            self, base_address, reader, n_bytes, packet_class, with_sum):
        offset = 0
        n_bytes_to_write = int(n_bytes)
        chksum = 0
        while n_bytes_to_write > 0:
            data_array = reader.read(
                min((n_bytes_to_write, UDP_MESSAGE_MAX_SIZE)))
            bytes_to_send = len(data_array)
            self._send_request(packet_class(
                base_address=base_address + offset, data=data_array))

            n_bytes_to_write -= bytes_to_send
            offset += bytes_to_send

            if with_sum:
                np_data = numpy.frombuffer(data_array, dtype="uint8")
                np_sum = int(numpy.sum(np_data.view("uint32")))
                chksum = (chksum + np_sum) & 0xFFFFFFFF

        self._finish()
        self.check_for_error()
        return chksum
