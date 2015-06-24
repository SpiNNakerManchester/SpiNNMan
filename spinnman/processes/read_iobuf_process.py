import functools
import struct
from collections import defaultdict

from spinnman.processes.get_cpu_info_process import GetCPUInfoProcess
from spinnman.model.io_buffer import IOBuffer
from spinnman.messages.scp.impl.scp_read_memory_request \
    import SCPReadMemoryRequest
from spinnman.processes.abstract_multi_connection_process \
    import AbstractMultiConnectionProcess


class ReadIOBufProcess(AbstractMultiConnectionProcess):
    """ A process for reading memory
    """

    def __init__(self, machine, connections, next_connection_selector=None):
        AbstractMultiConnectionProcess.__init__(
            self, connections, next_connection_selector)
        self._machine = machine

        # A dictionary of (x, y, p) -> str
        self._iobuf = defaultdict("")

    def handle_iobuf_response(self, x, y, p, base_address, response):
        (next_address, bytes_to_read) = struct.unpack_from(
            "<I8xI", response.data, response.offset)
        packet_bytes = response.length - 16
        if bytes_to_read < response.length - 16:
            offset = response.offset + 16
            self._iobuf[(x, y, p)] += response.data[
                offset:(offset + packet_bytes)]
        bytes_to_read -= packet_bytes


    def read_iobuf(self, chip_info, core_subsets):
        cpu_info_process = GetCPUInfoProcess(self._machine, self._connections)
        cpu_information = cpu_info_process.get_cpu_info(chip_info,
                                                        core_subsets)

        # Kick-start the reading of the IOBufs
        for cpu_info in cpu_information:
            self._send_request(
                SCPReadMemoryRequest(cpu_info.x, cpu_info.y,
                                     cpu_info.iobuf_address, 256),
                functools.partial(self.handle_iobuf_response,
                                  cpu_info.x, cpu_info.y, cpu_info.p,
                                  cpu_info.iobuf_address)

        self._finish()
        self.check_for_error()
        for core_subset in core_subsets:
            x = core_subset.x
            y = core_subset.y
            for p in core_subset.processor_ids:
                iobuf = self._iobuf[(x, y, p)]
                yield IOBuffer(x, y, p, iobuf)
