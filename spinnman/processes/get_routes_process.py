from spinnman.messages.scp.impl.scp_read_memory_request \
    import SCPReadMemoryRequest
from spinn_machine.multicast_routing_entry import MulticastRoutingEntry
from spinnman.processes.abstract_multi_connection_process \
    import AbstractMultiConnectionProcess
from spinnman import constants

import functools
import struct

# There are 1024 entries in a routing table
_N_ENTRIES = 1024

# 16 entries fit in a 256-byte read
_ENTRIES_PER_READ = 16

# 64 reads of 16 entries are required for 1024 entries
_N_READS = 64


class GetMultiCastRoutesProcess(AbstractMultiConnectionProcess):

    def __init__(self, connection_selector, app_id=None):
        AbstractMultiConnectionProcess.__init__(self, connection_selector)
        self._entries = [None] * _N_ENTRIES
        self._app_id = app_id

    def handle_read_response(self, offset, response):
        for route_no in range(_ENTRIES_PER_READ):
            (app_id, route, key, mask) = struct.unpack_from(
                "<2xBxIII", response.data, response.offset + (route_no * 16))
            if route < 0xFF000000 and (self._app_id is None or
                                       self._app_id == app_id):
                processor_ids = list()
                for processor_id in range(0, 26):
                    if (route & (1 << (6 + processor_id))) != 0:
                        processor_ids.append(processor_id)
                link_ids = list()
                for link_id in range(0, 6):
                    if (route & (1 << link_id)) != 0:
                        link_ids.append(link_id)
                self._entries[route_no + offset] = MulticastRoutingEntry(
                    key, mask, processor_ids, link_ids, False)

    def get_routes(self, x, y, base_address):

        # Create the read requests
        offset = 0
        for _ in range(_N_READS):
            self._send_request(
                SCPReadMemoryRequest(x, y, base_address + (offset * 16),
                                     constants.UDP_MESSAGE_MAX_SIZE),
                functools.partial(self.handle_read_response, offset))
            offset += _ENTRIES_PER_READ
        self._finish()
        self.check_for_error()

        return [entry for entry in self._entries if entry is not None]
