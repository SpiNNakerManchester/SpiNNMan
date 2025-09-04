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
from typing import Callable

from spinn_utilities.typing.coords import XYP

from spinnman.messages.scp.impl import ReadLink, ReadMemory
from spinnman.messages.scp.impl.read_memory import Response
from spinnman.constants import UDP_MESSAGE_MAX_SIZE
from spinnman.messages.scp.abstract_messages import AbstractSCPRequest

from .abstract_multi_connection_process import AbstractMultiConnectionProcess
from .abstract_multi_connection_process_connection_selector import (
    ConnectionSelector)


class ReadMemoryProcess(AbstractMultiConnectionProcess[Response]):
    """
    A process for reading memory on a SpiNNaker chip.
    """
    __slots__ = ("_view", )

    def __init__(self, connection_selector: ConnectionSelector):
        """
        :param connection_selector:
        """
        super().__init__(connection_selector)
        self._view = memoryview(b'')

    def __handle_response(self, offset: int, response: Response) -> None:
        self._view[offset:offset + response.length] = response.data[
            response.offset:response.offset + response.length]

    def read_memory(self, coordinates: XYP, base_address: int,
                    length: int) -> bytearray:
        """
        Read some memory from a core.

        :param coordinates:
        :param base_address:
        :param length:
        :returns: Data read from the core
        """
        return self._read_memory(
            base_address, length,
            functools.partial(ReadMemory, coordinates))

    def read_link_memory(self, coordinates: XYP, link: int,
                         base_address: int, length: int) -> bytearray:
        """
        Read some memory from the neighbour of a core.

        :param coordinates:
        :param link:
        :param base_address:
        :param length:
        :return: Data read over the link
        """
        return self._read_memory(
            base_address, length,
            functools.partial(ReadLink, coordinates, link))

    def _read_memory(
            self, base_address: int, length: int,
            packet_class: Callable[
                [int, int], AbstractSCPRequest[Response]]) -> bytearray:
        data = bytearray(length)
        self._view = memoryview(data)
        n_bytes = length
        offset = 0

        with self._collect_responses():
            while n_bytes > 0:
                bytes_to_get = min((n_bytes, UDP_MESSAGE_MAX_SIZE))
                self._send_request(
                    packet_class(base_address + offset, bytes_to_get),
                    functools.partial(self.__handle_response, offset))
                n_bytes -= bytes_to_get
                offset += bytes_to_get

        return data
