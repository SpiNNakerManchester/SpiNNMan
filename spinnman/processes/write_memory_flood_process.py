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

import math
from spinnman.messages.scp.impl import (
    FloodFillEnd, FloodFillStart, FloodFillData)
from .abstract_multi_connection_process import AbstractMultiConnectionProcess
from spinnman.constants import UDP_MESSAGE_MAX_SIZE


class WriteMemoryFloodProcess(AbstractMultiConnectionProcess):
    """
    A process for writing memory on multiple SpiNNaker chips at once.
    """
    __slots__ = []

    def __init__(self, next_connection_selector):
        AbstractMultiConnectionProcess.__init__(
            self, next_connection_selector, n_channels=3,
            intermediate_channel_waits=2)

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
                                    data, offset, n_bytes=None):
        """
        :param int nearest_neighbour_id:
        :param int base_address:
        :param data:
        :type data: bytes or bytearray
        :param int offset:
        :param int n_bytes:
        """
        # pylint: disable=too-many-arguments
        if n_bytes is None:
            n_bytes = len(data)
        self._start_flood_fill(n_bytes, nearest_neighbour_id)

        data_offset = offset
        offset = base_address
        block_no = 0
        while n_bytes > 0:
            bytes_to_send = min((int(n_bytes), UDP_MESSAGE_MAX_SIZE))

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
                                 reader, n_bytes):
        """
        :param int nearest_neighbour_id:
        :param int base_address:
        :param reader:
        :type reader: ~io.RawIOBase or ~io.BufferedIOBase
        :param int n_bytes:
        """
        self._start_flood_fill(n_bytes, nearest_neighbour_id)

        offset = base_address
        block_no = 0
        while n_bytes > 0:
            bytes_to_send = min((int(n_bytes), UDP_MESSAGE_MAX_SIZE))
            data_array = reader.read(bytes_to_send)

            self._send_request(FloodFillData(
                nearest_neighbour_id, block_no, offset,
                data_array, 0, len(data_array)))

            block_no += 1
            n_bytes -= bytes_to_send
            offset += bytes_to_send
        self._finish()
        self.check_for_error()

        self._end_flood_fill(nearest_neighbour_id)
