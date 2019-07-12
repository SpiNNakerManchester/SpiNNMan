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
import functools
from spinnman.messages.scp.impl import ReadMemory
from spinn_machine import MulticastRoutingEntry, Router
from .abstract_multi_connection_process import AbstractMultiConnectionProcess
from spinnman.constants import UDP_MESSAGE_MAX_SIZE

# There are 1024 entries in a routing table
_N_ENTRIES = 1024

# 16 entries fit in a 256-byte read
_ENTRIES_PER_READ = 16

# 64 reads of 16 entries are required for 1024 entries
_N_READS = 64

_ROUTE_ENTRY_PATTERN = struct.Struct("<2xBxIII")


class GetMultiCastRoutesProcess(AbstractMultiConnectionProcess):
    """ A process for reading the multicast routing table of a SpiNNaker chip.
    """
    __slots__ = [
        "_app_id",
        "_entries"]

    def __init__(self, connection_selector, app_id=None):
        super(GetMultiCastRoutesProcess, self).__init__(connection_selector)
        self._entries = [None] * _N_ENTRIES
        self._app_id = app_id

    def _add_routing_entry(self, route_no, offset, app_id, route, key, mask):
        # pylint: disable=too-many-arguments
        if route >= 0xFF000000:
            return
        if self._app_id is not None and self._app_id != app_id:
            return

        # Convert bit-set into list of (set) IDs
        processor_ids, link_ids = \
            Router.convert_spinnaker_route_to_routing_ids(route)

        self._entries[route_no + offset] = MulticastRoutingEntry(
            key, mask, processor_ids, link_ids, False)

    def handle_read_response(self, offset, response):
        for route_no in range(_ENTRIES_PER_READ):
            entry = _ROUTE_ENTRY_PATTERN.unpack_from(
                response.data,
                response.offset + route_no * _ROUTE_ENTRY_PATTERN.size)
            self._add_routing_entry(route_no, offset, *entry)

    def get_routes(self, x, y, base_address):

        # Create the read requests
        offset = 0
        for _ in range(_N_READS):
            self._send_request(
                ReadMemory(
                    x, y, base_address + (offset * 16), UDP_MESSAGE_MAX_SIZE),
                functools.partial(self.handle_read_response, offset))
            offset += _ENTRIES_PER_READ
        self._finish()
        self.check_for_error()

        return [entry for entry in self._entries if entry is not None]
