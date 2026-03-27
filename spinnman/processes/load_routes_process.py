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
from typing import Collection

from spinn_machine import Router
from spinn_machine.multicast_routing_entry import MulticastRoutingEntry

from spinnman.exceptions import SpinnmanInvalidParameterException
from spinnman.messages.scp.impl import RouterInit, RouterAlloc
from spinnman.messages.scp.impl.router_alloc import RouterAllocResponse

from .abstract_multi_connection_process import AbstractMultiConnectionProcess
from .abstract_multi_connection_process_connection_selector import (
    ConnectionSelector)
from .write_memory_process import WriteMemoryProcess

_ROUTE_PATTERN = struct.Struct("<H2xIII")
_END_PATTERN = struct.Struct("<IIII")
_TABLE_ADDRESS = 0x67800000


class LoadMultiCastRoutesProcess(AbstractMultiConnectionProcess):
    """
    A process for loading the multicast routing table on a SpiNNaker chip.
    """
    __slots__ = ("_base_address", )

    def __init__(self, connection_selector: ConnectionSelector):
        """
        :param connection_selector:
        """
        super().__init__(connection_selector)
        self._base_address = 0

    def __handle_router_alloc_response(
            self, response: RouterAllocResponse) -> None:
        self._base_address = response.base_address

    def load_routes(
            self, x: int, y: int, routes: Collection[MulticastRoutingEntry],
            app_id: int) -> None:
        """
        Converts the routing entries to Machine format
        and loads then onto the Chip.

        :param x:
        :param y:
        :param routes:
        :param app_id:
        """
        # Create the routing data - 16 bytes per entry plus one for the end
        # entry
        routing_data = bytearray(16 * (len(routes) + 1))
        n_entries = 0
        for route in routes:
            route_entry = \
                Router.convert_routing_table_entry_to_spinnaker_route(route)

            _ROUTE_PATTERN.pack_into(
                routing_data, n_entries * 16, n_entries,
                route_entry, route.key, route.mask)
            n_entries += 1

        # Add an entry to mark the end
        _END_PATTERN.pack_into(
            routing_data, n_entries * 16,
            0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF)

        # Upload the data
        process = WriteMemoryProcess(self._conn_selector)
        process.write_memory_from_bytearray(
            (x, y, 0), _TABLE_ADDRESS, routing_data, 0, len(routing_data))

        # Allocate space in the router table
        with self._collect_responses():
            self._send_request(RouterAlloc(x, y, app_id, n_entries),
                               self.__handle_router_alloc_response)
        if self._base_address == 0:
            raise SpinnmanInvalidParameterException(
                "Allocation base address", str(self._base_address),
                "Not enough space to allocate the entries")

        # Load the entries
        with self._collect_responses():
            self._send_request(RouterInit(
                x, y, n_entries, _TABLE_ADDRESS, self._base_address, app_id))
