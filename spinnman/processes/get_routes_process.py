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
    """
    A process for reading the multicast routing table of a SpiNNaker chip.
    """
    __slots__ = [
        "_app_id",
        "_entries"]

    def __init__(self, connection_selector, app_id=None):
        """
        :param connection_selector:
        :type connection_selector:
            AbstractMultiConnectionProcessConnectionSelector
        :param int app_id:
        """
        super().__init__(connection_selector)
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

    def __handle_response(self, offset, response):
        for route_no in range(_ENTRIES_PER_READ):
            entry = _ROUTE_ENTRY_PATTERN.unpack_from(
                response.data,
                response.offset + route_no * _ROUTE_ENTRY_PATTERN.size)
            self._add_routing_entry(route_no, offset, *entry)

    def get_routes(self, x, y, base_address):
        """
        :param int x:
        :param int y:
        :param int base_address:
        :rtype: list(~spinn_machine.MulticastRoutingEntry)
        """
        # Create the read requests
        offset = 0
        for _ in range(_N_READS):
            self._send_request(
                ReadMemory(
                    x, y, base_address + (offset * 16), UDP_MESSAGE_MAX_SIZE),
                functools.partial(self.__handle_response, offset))
            offset += _ENTRIES_PER_READ
        self._finish()
        self.check_for_error()

        return [entry for entry in self._entries if entry is not None]
