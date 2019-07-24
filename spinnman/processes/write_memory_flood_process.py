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

import math
from spinnman.messages.scp.impl import (
    FloodFillEnd, FloodFillStart, FloodFillData)
from .abstract_multi_connection_process import AbstractMultiConnectionProcess
from spinnman.constants import UDP_MESSAGE_MAX_SIZE


class WriteMemoryFloodProcess(AbstractMultiConnectionProcess):
    """ A process for writing memory on multiple SpiNNaker chips at once.
    """
    __slots__ = []

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
