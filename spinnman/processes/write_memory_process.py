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
from typing import BinaryIO, Callable
import numpy
from numpy import uint8, uint32
from spinn_utilities.typing.coords import XYP
from spinnman.messages.scp.abstract_messages import AbstractSCPRequest
from spinnman.messages.scp.impl import WriteLink, WriteMemory
from spinnman.messages.scp.impl import CheckOKResponse
from spinnman.constants import UDP_MESSAGE_MAX_SIZE
from .abstract_multi_connection_process import AbstractMultiConnectionProcess

_UNSIGNED_WORD = 0xFFFFFFFF


class WriteMemoryProcess(AbstractMultiConnectionProcess[CheckOKResponse]):
    """
    A process for writing memory on a SpiNNaker chip.
    """
    __slots__ = ()

    def write_memory_from_bytearray(
            self, coordinates: XYP, base_address: int, data: bytes,
            offset: int, n_bytes: int, get_sum: bool = False) -> int:
        """
        Writes memory onto a SpiNNaker chip from a bytearray.

        :param coordinates:
            The X,Y,P coordinates of the core that will write to memory.
        :param base_address: the address in SDRAM to start writing
        :param data: the data to write
        :param offset: where in the data to start writing from
        :param n_bytes: how much data to write
        :param get_sum: whether to return a checksum or 0
        :return: the data checksum or 0 if get_sum is False
        """
        return self._write_memory_from_bytearray(
            base_address, data, offset, n_bytes,
            functools.partial(WriteMemory, coordinates), get_sum)

    def write_link_memory_from_bytearray(
            self, coordinates: XYP, link: int, base_address: int, data: bytes,
            offset: int, n_bytes: int, get_sum: bool = False) -> int:
        """
        Writes memory onto a neighbour of a SpiNNaker chip from a bytearray.

        :param coordinates:
            The X,Y,P coordinates of the core that will write to its
            neighbour's memory.
        :param link:
            Along which link is the neighbour.
        :param base_address: the address in SDRAM to start writing
        :param data: the data to write
        :param offset: where in the data to start writing from
        :param n_bytes: how much data to write
        :param get_sum: whether to return a checksum or 0
        :return: the data checksum or 0 if get_sum is False
        """
        return self._write_memory_from_bytearray(
            base_address, data, offset, n_bytes,
            functools.partial(WriteLink, coordinates, link), get_sum)

    def write_memory_from_reader(
            self, coordinates: XYP, base_address: int, reader: BinaryIO,
            n_bytes: int, get_sum: bool = False) -> int:
        """
        Writes memory onto a SpiNNaker chip from a reader.

        :param coordinates:
            The X,Y,P coordinates of the core that will write to memory.
        :param base_address: the address in SDRAM to start writing
        :param reader: the readable object containing the data to write
        :param n_bytes: how much data to write
        :param get_sum: whether to return a checksum or 0
        :return: the data checksum or 0 if get_sum is False
        """
        return self._write_memory_from_reader(
            base_address, reader, n_bytes,
            functools.partial(WriteMemory, coordinates), get_sum)

    def write_link_memory_from_reader(
            self, coordinates: XYP, link: int, base_address: int,
            reader: BinaryIO, n_bytes: int, get_sum: bool = False) -> int:
        """
        Writes memory onto a neighbour of a SpiNNaker chip from a reader.

        :param coordinates:
            The X,Y,P coordinates of the core that will write to its
            neighbour's memory. The P coordinate is normally 0; no reason to
            not use SCAMP for this.
        :param link:
            Along which link is the neighbour.
        :param base_address: the address in SDRAM to start writing
        :param reader: the readable object containing the data to write
        :param n_bytes: how much data to write
        :param get_sum: whether to return a checksum or 0
        :return: the data checksum or 0 if get_sum is False
        """
        return self._write_memory_from_reader(
            base_address, reader, n_bytes,
            functools.partial(WriteLink, coordinates, link), get_sum)

    def _write_memory_from_bytearray(
            self, base_address: int, data: bytes, data_offset: int,
            n_bytes: int, packet_class: Callable[
                [int, bytes], AbstractSCPRequest[CheckOKResponse]],
            get_sum: bool) -> int:
        offset = 0
        n_bytes_to_write = int(n_bytes)
        with self._collect_responses():
            while n_bytes_to_write > 0:
                bytes_to_send = min(n_bytes_to_write, UDP_MESSAGE_MAX_SIZE)
                data_array = data[data_offset:data_offset + bytes_to_send]

                self._send_request(
                    packet_class(base_address + offset, data_array))

                n_bytes_to_write -= bytes_to_send
                offset += bytes_to_send
                data_offset += bytes_to_send
        if not get_sum:
            return 0
        np_data = numpy.array(data, dtype=uint8)
        np_sum = int(numpy.sum(np_data.view(uint32), dtype=uint32))
        return np_sum & _UNSIGNED_WORD

    def _write_memory_from_reader(
            self, base_address: int, reader: BinaryIO, n_bytes: int,
            packet_class: Callable[
                [int, bytes], AbstractSCPRequest[CheckOKResponse]],
            with_sum: bool) -> int:
        offset = 0
        n_bytes_to_write = int(n_bytes)
        chksum = 0
        with self._collect_responses():
            while n_bytes_to_write > 0:
                data_array = reader.read(
                    min(n_bytes_to_write, UDP_MESSAGE_MAX_SIZE))
                bytes_to_send = len(data_array)
                self._send_request(packet_class(
                    base_address + offset, data_array))

                n_bytes_to_write -= bytes_to_send
                offset += bytes_to_send

                if with_sum:
                    np_data = numpy.frombuffer(data_array, dtype=uint8)
                    np_sum = int(numpy.sum(np_data.view(uint32)))
                    chksum = (chksum + np_sum) & _UNSIGNED_WORD

        return chksum
