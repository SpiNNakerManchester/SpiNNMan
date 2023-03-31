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
from spinnman.messages.scp.impl import ReadLink, ReadMemory
from .abstract_multi_connection_process import AbstractMultiConnectionProcess
from spinnman.constants import UDP_MESSAGE_MAX_SIZE


class ReadMemoryProcess(AbstractMultiConnectionProcess):
    """
    A process for reading memory on a SpiNNaker chip.
    """
    __slots__ = [
        "_view"]

    def __init__(self, connection_selector):
        """
        :param connection_selector:
        :type connection_selector:
            AbstractMultiConnectionProcessConnectionSelector
        """
        super().__init__(connection_selector)
        self._view = None

    def __handle_response(self, offset, response):
        self._view[offset:offset + response.length] = response.data[
            response.offset:response.offset + response.length]

    def read_memory(self, x, y, p, base_address, length):
        """
        :param int x:
        :param int y:
        :param int p:
        :param int base_address:
        :param int length:
        :rtype: bytearray
        """
        return self._read_memory(
            base_address, length,
            functools.partial(ReadMemory, x=x, y=y, cpu=p))

    def read_link_memory(self, x, y, p, link, base_address, length):
        """
        :param int x:
        :param int y:
        :param int p:
        :param int link:
        :param int base_address:
        :param int length:
        :rtype: bytearray
        """
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
            self._send_request(
                packet_class(
                    base_address=base_address + offset, size=bytes_to_get),
                functools.partial(self.__handle_response, offset))
            n_bytes -= bytes_to_get
            offset += bytes_to_get

        self._finish()
        self.check_for_error()

        return data
