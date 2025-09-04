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

import struct
from functools import partial
from typing import List, Optional

from spinn_machine import MulticastRoutingEntry, RoutingEntry
from spinnman.messages.scp.impl.read_memory import ReadMemory, Response
from spinnman.constants import UDP_MESSAGE_MAX_SIZE

from .abstract_multi_connection_process import AbstractMultiConnectionProcess
from .abstract_multi_connection_process_connection_selector import (
    ConnectionSelector)

# There are 1024 entries in a routing table
_N_ENTRIES = 1024

# 16 entries fit in a 256-byte read
_ENTRIES_PER_READ = 16

# 64 reads of 16 entries are required for 1024 entries
_N_READS = 64

_ROUTE_ENTRY_PATTERN = struct.Struct("<2xBxIII")


class GetMultiCastRoutesProcess(AbstractMultiConnectionProcess[Response]):
    """
    A process for reading the multicast routing table of a SpiNNaker chip.
    """
    __slots__ = (
        "_app_id",
        "_entries")

    def __init__(self, connection_selector: ConnectionSelector,
                 app_id: Optional[int] = None):
        """
        :param connection_selector:
        :param app_id:
        """
        super().__init__(connection_selector)
        self._entries: List[Optional[MulticastRoutingEntry]] = \
            [None] * _N_ENTRIES
        self._app_id = app_id

    def _add_routing_entry(
            self, route_no: int, offset: int, app_id: int, route: int,
            key: int, mask: int) -> None:
        if route >= 0xFF000000:
            return
        if self._app_id is not None and self._app_id != app_id:
            return

        self._entries[route_no + offset] = MulticastRoutingEntry(
            key, mask, RoutingEntry(spinnaker_route=route))

    def __handle_response(self, offset: int, response: Response) -> None:
        for route_no in range(_ENTRIES_PER_READ):
            entry = _ROUTE_ENTRY_PATTERN.unpack_from(
                response.data,
                response.offset + route_no * _ROUTE_ENTRY_PATTERN.size)
            self._add_routing_entry(route_no, offset, *entry)

    def get_routes(self, x: int, y: int,
                   base_address: int) -> List[MulticastRoutingEntry]:
        """
        :param x:
        :param y:
        :param base_address:
        :returns: The Routes read from the scamp chip
        """
        # Create the read requests
        offset = 0
        scamp_coords = x, y, 0
        with self._collect_responses():
            for _ in range(_N_READS):
                self._send_request(
                    ReadMemory(
                        scamp_coords, base_address + (offset * 16),
                        UDP_MESSAGE_MAX_SIZE),
                    partial(self.__handle_response, offset))
                offset += _ENTRIES_PER_READ

        return [entry for entry in self._entries if entry is not None]
