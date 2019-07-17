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
from spinnman.messages.scp.impl import ReadLink, ReadMemory
from .abstract_multi_connection_process import AbstractMultiConnectionProcess
from spinnman.constants import UDP_MESSAGE_MAX_SIZE


class ReadMemoryProcess(AbstractMultiConnectionProcess):
    """ A process for reading memory on a SpiNNaker chip.
    """
    __slots__ = [
        "_view"]

    def __init__(self, connection_selector):
        super(ReadMemoryProcess, self).__init__(connection_selector)
        self._view = None

    def handle_response(self, offset, response):
        self._view[offset:offset + response.length] = response.data[
            response.offset:response.offset + response.length]

    def read_memory(self, x, y, p, base_address, length):
        return self._read_memory(
            base_address, length,
            functools.partial(ReadMemory, x=x, y=y, cpu=p))

    def read_link_memory(self, x, y, p, link, base_address, length):
        return self._read_memory(
            base_address, length,
            functools.partial(ReadLink, x=x, y=y, cpu=p, link=link))

    def _read_memory(self, base_address, length, packet_class):
        data = bytearray(length)
        self._view = memoryview(data)
        n_bytes = length
        offset = 0
        while n_bytes > 0:
            bytes_to_get = min((n_bytes, UDP_MESSAGE_MAX_SIZE))
            response_handler = functools.partial(self.handle_response, offset)
            self._send_request(
                packet_class(
                    base_address=base_address + offset, size=bytes_to_get),
                response_handler)
            n_bytes -= bytes_to_get
            offset += bytes_to_get

        self._finish()
        self.check_for_error()

        return data
