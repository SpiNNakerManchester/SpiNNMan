import functools
import struct
from collections import defaultdict, OrderedDict

from spinnman.model import IOBuffer
from spinnman.utilities.utility_functions import get_vcpu_address
from spinnman.messages.scp.impl import ReadMemory
from .abstract_multi_connection_process import AbstractMultiConnectionProcess
from spinnman.constants import UDP_MESSAGE_MAX_SIZE, CPU_IOBUF_ADDRESS_OFFSET

_ENCODING = "ascii"


class ReadIOBufProcess(AbstractMultiConnectionProcess):
    """ A process for reading memory
    """

    def __init__(self, connection_selector):
        AbstractMultiConnectionProcess.__init__(self, connection_selector)

        # A dictionary of (x, y, p) -> iobuf address
        self._iobuf_address = dict()

        # A dictionary of (x, y, p) -> OrderedDict(n) -> bytearray
        self._iobuf = defaultdict(OrderedDict)

        # A dictionary of (x, y, p) -> OrderedDict(n) -> memoryview
        self._iobuf_view = defaultdict(OrderedDict)

        # A list of extra reads that need to be done as a result of the first
        # read = list of (x, y, p, n, base_address, size, offset)
        self._extra_reads = list()

        # A list of next reads that need to be done as a result of the first
        # read = list of (x, y, p, n, next_address, first_read_size)
        self._next_reads = list()

    def handle_iobuf_address_response(self, iobuf_size, x, y, p, response):
        iobuf_address = struct.unpack_from(
            "<I", response.data, response.offset)[0]
        if iobuf_address != 0:
            first_read_size = min((iobuf_size + 16, UDP_MESSAGE_MAX_SIZE))
            self._next_reads.append((
                x, y, p, 0, iobuf_address, first_read_size))

    def _request_iobuf_region(self, region):
        (x, y, p, n, next_address, first_read_size) = region
        self._send_request(
            ReadMemory(x, y, next_address, first_read_size),
            functools.partial(self.handle_first_iobuf_response,
                              x, y, p, n, next_address, first_read_size))

    def handle_first_iobuf_response(self, x, y, p, n, base_address,
                                    first_read_size, response):

        # Unpack the iobuf header
        (next_address, bytes_to_read) = struct.unpack_from(
            "<I8xI", response.data, response.offset)

        # Create a buffer for the data
        data = bytearray(bytes_to_read)
        view = memoryview(data)
        self._iobuf[(x, y, p)][n] = data
        self._iobuf_view[(x, y, p)][n] = view

        # Put the data from this packet into the buffer
        packet_bytes = response.length - 16
        if packet_bytes > bytes_to_read:
            packet_bytes = bytes_to_read
        offset = response.offset + 16
        if packet_bytes > 0:
            view[0:packet_bytes] = response.data[
                offset:(offset + packet_bytes)]

        bytes_to_read -= packet_bytes
        base_address += packet_bytes + 16
        read_offset = packet_bytes

        # While more reads need to be done to read the data
        while bytes_to_read > 0:

            # Read the next bit of memory making up the buffer
            next_bytes_to_read = min((bytes_to_read, UDP_MESSAGE_MAX_SIZE))
            self._extra_reads.append((x, y, p, n, base_address,
                                      next_bytes_to_read, read_offset))
            base_address += next_bytes_to_read
            read_offset += next_bytes_to_read
            bytes_to_read -= next_bytes_to_read

        # If there is another IOBuf buffer, read this next
        if next_address != 0:
            self._next_reads.append((x, y, p, n + 1, next_address,
                                     first_read_size))

    def _request_iobuf_region_tail(self, extra_region):
        (x, y, p, n, base_address, size, offset) = extra_region
        self._send_request(
            ReadMemory(x, y, base_address, size),
            functools.partial(self.handle_extra_iobuf_response,
                              x, y, p, n, offset))

    def handle_extra_iobuf_response(self, x, y, p, n, offset, response):
        view = self._iobuf_view[(x, y, p)][n]
        view[offset:offset + response.length] = response.data[
            response.offset:response.offset + response.length]

    def _request_iobuf_address(self, iobuf_size, x, y, p):
        base_address = get_vcpu_address(p) + CPU_IOBUF_ADDRESS_OFFSET
        self._send_request(
            ReadMemory(x, y, base_address, 4),
            functools.partial(self.handle_iobuf_address_response,
                              iobuf_size, x, y, p))

    def read_iobuf(self, iobuf_size, core_subsets):
        # Get the iobuf address for each core
        for core_subset in core_subsets:
            x = core_subset.x
            y = core_subset.y
            for p in core_subset.processor_ids:
                self._request_iobuf_address(iobuf_size, x, y, p)
        self._finish()
        self.check_for_error()

        # Run rounds of the process until reading is complete
        while len(self._extra_reads) > 0 or len(self._next_reads) > 0:
            # Process the extra iobuf reads needed
            while self._extra_reads:
                self._request_iobuf_region_tail(self._extra_reads.pop())

            # Process the next iobuf reads needed
            while self._next_reads:
                self._request_iobuf_region(self._next_reads.pop())

            # Finish this round
            self._finish()

        self.check_for_error()

        for core_subset in core_subsets:
            x = core_subset.x
            y = core_subset.y
            for p in core_subset.processor_ids:
                iobufs = self._iobuf[(x, y, p)]
                iobuf = ""
                for item in iobufs.itervalues():
                    iobuf += item.decode(_ENCODING)

                yield IOBuffer(x, y, p, iobuf)
