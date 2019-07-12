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

import struct
from spinn_machine import Router
from spinnman.exceptions import SpinnmanInvalidParameterException
from spinnman.messages.scp.impl import RouterInit, RouterAlloc
from .abstract_multi_connection_process import AbstractMultiConnectionProcess
from .write_memory_process import WriteMemoryProcess

_ROUTE_PATTERN = struct.Struct("<H2xIII")
_END_PATTERN = struct.Struct("<IIII")


class LoadMultiCastRoutesProcess(AbstractMultiConnectionProcess):
    """ A process for loading the multicast routing table on a SpiNNaker\
        chip.
    """
    __slots__ = [
        "_base_address"]

    def __init__(self, connection_selector):
        super(LoadMultiCastRoutesProcess, self).__init__(connection_selector)
        self._base_address = None

    def handle_router_alloc_response(self, response):
        self._base_address = response.base_address

    def load_routes(self, x, y, routes, app_id):
        # Create the routing data - 16 bytes per entry plus one for the end
        # entry
        routing_data = bytearray(16 * (len(routes) + 1))
        n_entries = 0
        for route in routes:
            route_entry = \
                Router.convert_routing_table_entry_to_spinnaker_route(route)

            _ROUTE_PATTERN.pack_into(
                routing_data, n_entries * 16, n_entries,
                route_entry, route.routing_entry_key, route.mask)
            n_entries += 1

        # Add an entry to mark the end
        _END_PATTERN.pack_into(
            routing_data, n_entries * 16,
            0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF)

        # Upload the data
        table_address = 0x67800000
        process = WriteMemoryProcess(self._next_connection_selector)
        process.write_memory_from_bytearray(
            x, y, 0, table_address, routing_data, 0, len(routing_data))

        # Allocate space in the router table
        self._send_request(RouterAlloc(x, y, app_id, n_entries),
                           self.handle_router_alloc_response)
        self._finish()
        self.check_for_error()
        if self._base_address == 0:
            raise SpinnmanInvalidParameterException(
                "Allocation base address", str(self._base_address),
                "Not enough space to allocate the entries")

        # Load the entries
        self._send_request(
            RouterInit(
                x, y, n_entries, table_address, self._base_address, app_id))
        self._finish()
        self.check_for_error()
