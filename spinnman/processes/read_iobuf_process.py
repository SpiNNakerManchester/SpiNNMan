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

from dataclasses import dataclass
import functools
import struct
from collections import defaultdict
from typing import Dict, Iterable, List
from spinn_utilities.typing.coords import XYP
from spinn_machine import CoreSubsets
from spinnman.model import IOBuffer
from spinnman.utilities.utility_functions import get_vcpu_address
from spinnman.messages.scp.impl.read_memory import ReadMemory, Response
from spinnman.constants import UDP_MESSAGE_MAX_SIZE, CPU_IOBUF_ADDRESS_OFFSET
from .abstract_multi_connection_process import AbstractMultiConnectionProcess
from .abstract_multi_connection_process_connection_selector import (
    ConnectionSelector)


@dataclass(frozen=True)
class _RegionTail:
    scamp_coords: XYP
    core_coords: XYP
    n: int
    base_address: int
    size: int
    offset: int


@dataclass(frozen=True)
class _NextRegion:
    scamp_coords: XYP
    core_coords: XYP
    n: int
    next_address: int
    first_read_size: int

    def next_at(self, address: int) -> '_NextRegion':
        """
        :param address:
        :returns: The next region. (ID one greater than this region)
        """
        return _NextRegion(
            self.scamp_coords, self.core_coords, self.n + 1, address,
            self.first_read_size)

    def tail(self, address: int, size: int, offset: int) -> _RegionTail:
        """

        :param address:
        :param size:
        :param offset:
        :returns: The tail of the this region.
        """
        return _RegionTail(
            self.scamp_coords, self.core_coords, self.n, address, size, offset)


_ENCODING = "ascii"
_ONE_WORD = struct.Struct("<I")
_FIRST_IOBUF = struct.Struct("<I8xI")


class ReadIOBufProcess(AbstractMultiConnectionProcess[Response]):
    """
    A process for reading IOBUF memory (mostly log messages) from a
    SpiNNaker core.
    """
    __slots__ = (
        "_extra_reads",
        "_iobuf",
        "_iobuf_address",
        "_iobuf_view",
        "_next_reads")

    def __init__(self, connection_selector: ConnectionSelector) -> None:
        """
        :param connection_selector:
        """
        super().__init__(connection_selector)

        # A dictionary of (x, y, p) -> iobuf address
        self._iobuf_address: Dict[XYP, int] = dict()

        # A dictionary of (x, y, p) -> OrderedDict(n) -> bytearray
        self._iobuf: Dict[XYP, Dict[int, bytes]] = defaultdict(dict)

        # A dictionary of (x, y, p) -> OrderedDict(n) -> memoryview
        self._iobuf_view: Dict[XYP, Dict[int, memoryview]] = defaultdict(dict)

        # A list of extra reads that need to be done as a result of the first
        # read = list of (x, y, p, n, base_address, size, offset)
        self._extra_reads: List[_RegionTail] = list()

        # A list of next reads that need to be done as a result of the first
        # read = list of (x, y, p, n, next_address, first_read_size)
        self._next_reads: List[_NextRegion] = list()

    def _request_iobuf_address(
            self, iobuf_size: int, x: int, y: int, p: int) -> None:
        scamp_coords = (x, y, 0)
        base_address = get_vcpu_address(p) + CPU_IOBUF_ADDRESS_OFFSET
        self._send_request(
            ReadMemory(scamp_coords, base_address, 4),
            functools.partial(self.__handle_iobuf_address_response,
                              iobuf_size, scamp_coords, (x, y, p)))

    def __handle_iobuf_address_response(
            self, iobuf_size: int, scamp_coords: XYP, xyp: XYP,
            response: Response) -> None:
        iobuf_address, = _ONE_WORD.unpack_from(response.data, response.offset)
        if iobuf_address != 0:
            first_read_size = min((iobuf_size + 16, UDP_MESSAGE_MAX_SIZE))
            self._next_reads.append(_NextRegion(
                scamp_coords, xyp, 0, iobuf_address, first_read_size))

    def _request_iobuf_region_tail(self, tail: _RegionTail) -> None:
        self._send_request(
            ReadMemory(tail.scamp_coords, tail.base_address, tail.size),
            functools.partial(
                self.__handle_extra_iobuf_response, tail))

    def __handle_extra_iobuf_response(
            self, tail: _RegionTail, response: Response) -> None:
        view = self._iobuf_view[tail.core_coords][tail.n]
        base = tail.offset
        view[base:base + response.length] = response.data[
            response.offset:response.offset + response.length]

    def _request_iobuf_region(self, region: _NextRegion) -> None:
        self._send_request(
            ReadMemory(region.scamp_coords, region.next_address,
                       region.first_read_size),
            functools.partial(self.__handle_first_iobuf_response, region))

    def __handle_first_iobuf_response(
            self, region: _NextRegion, response: Response) -> None:
        base_address = region.next_address

        # Unpack the iobuf header
        (next_address, bytes_to_read) = _FIRST_IOBUF.unpack_from(
            response.data, response.offset)

        # Create a buffer for the data
        data = bytearray(bytes_to_read)
        view = memoryview(data)
        self._iobuf[region.core_coords][region.n] = data
        self._iobuf_view[region.core_coords][region.n] = view

        # Put the data from this packet into the buffer
        packet_bytes = response.length - 16
        if packet_bytes > bytes_to_read:
            packet_bytes = bytes_to_read
        if packet_bytes > 0:
            offset = response.offset + 16
            view[0:packet_bytes] = response.data[offset:offset + packet_bytes]

        bytes_to_read -= packet_bytes
        base_address += packet_bytes + 16
        read_offset = packet_bytes

        # While more reads need to be done to read the data
        while bytes_to_read > 0:
            # Read the next bit of memory making up the buffer
            next_bytes_to_read = min((bytes_to_read, UDP_MESSAGE_MAX_SIZE))
            self._extra_reads.append(region.tail(
                base_address, next_bytes_to_read, read_offset))
            base_address += next_bytes_to_read
            read_offset += next_bytes_to_read
            bytes_to_read -= next_bytes_to_read

        # If there is another IOBuf buffer, read this next
        if next_address != 0:
            self._next_reads.append(region.next_at(next_address))

    def read_iobuf(
            self, iobuf_size: int,
            core_subsets: CoreSubsets) -> Iterable[IOBuffer]:
        """
        :param iobuf_size:
        :param core_subsets:
        :returns: IOBuffer for each core in order
        """
        # Get the iobuf address for each core
        with self._collect_responses():
            for core_subset in core_subsets:
                x, y = core_subset.x, core_subset.y
                for p in core_subset.processor_ids:
                    self._request_iobuf_address(iobuf_size, x, y, p)

        # Run rounds of the process until reading is complete
        while self._extra_reads or self._next_reads:
            with self._collect_responses():
                # Process the extra iobuf reads needed
                while self._extra_reads:
                    self._request_iobuf_region_tail(self._extra_reads.pop())

                # Process the next iobuf reads needed
                while self._next_reads:
                    self._request_iobuf_region(self._next_reads.pop())

        for core_subset in core_subsets:
            x, y = core_subset.x, core_subset.y
            for p in core_subset.processor_ids:
                iobuf = ""
                for item in self._iobuf[x, y, p].values():
                    iobuf += item.decode(_ENCODING)
                yield IOBuffer(x, y, p, iobuf)
