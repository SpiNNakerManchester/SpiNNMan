from spinnman.messages.scp.impl import \
    FloodFillEnd, FloodFillStart, FloodFillData
from .abstract_multi_connection_process import AbstractMultiConnectionProcess
from spinnman.constants import UDP_MESSAGE_MAX_SIZE

import math


class WriteMemoryFloodProcess(AbstractMultiConnectionProcess):
    """ A process for writing memory
    """

    def __init__(self, connection_selector):
        AbstractMultiConnectionProcess.__init__(self, connection_selector)

    def _start_flood_fill(self, n_bytes, nearest_neighbour_id):
        n_blocks = int(math.ceil(math.ceil(n_bytes / 4.0) /
                                 UDP_MESSAGE_MAX_SIZE))
        self._send_request(
            FloodFillStart(nearest_neighbour_id, n_blocks))
        self._finish()
        self.check_for_error()

    def _end_flood_fill(self, nearest_neighbour_id):
        self._send_request(FloodFillEnd(nearest_neighbour_id))
        self._finish()
        self.check_for_error()

    def write_memory_from_bytearray(self, nearest_neighbour_id, base_address,
                                    data, offset, n_bytes):
        self._start_flood_fill(n_bytes, nearest_neighbour_id)

        data_offset = offset
        offset = base_address
        block_no = 0
        while n_bytes > 0:

            bytes_to_send = int(n_bytes)
            if bytes_to_send > UDP_MESSAGE_MAX_SIZE:
                bytes_to_send = UDP_MESSAGE_MAX_SIZE

            self._send_request(FloodFillData(
                nearest_neighbour_id, block_no, offset,
                data, data_offset, bytes_to_send))

            block_no += 1
            n_bytes -= bytes_to_send
            offset += bytes_to_send
            data_offset += bytes_to_send
        self._finish()
        self.check_for_error()

        self._end_flood_fill(nearest_neighbour_id)

    def write_memory_from_reader(self, nearest_neighbour_id, base_address,
                                 data, n_bytes):
        self._start_flood_fill(n_bytes, nearest_neighbour_id)

        offset = base_address
        block_no = 0
        while n_bytes > 0:

            bytes_to_send = int(n_bytes)
            if bytes_to_send > UDP_MESSAGE_MAX_SIZE:
                bytes_to_send = UDP_MESSAGE_MAX_SIZE
            data_array = data.read(bytes_to_send)

            self._send_request(FloodFillData(
                nearest_neighbour_id, block_no, offset,
                data_array, 0, len(data_array)))

            block_no += 1
            n_bytes -= bytes_to_send
            offset += bytes_to_send
        self._finish()
        self.check_for_error()

        self._end_flood_fill(nearest_neighbour_id)
