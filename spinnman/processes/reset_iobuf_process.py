import functools
import struct

from spinnman.processes.get_cpu_info_process import GetCPUInfoProcess
from spinnman.model.io_buffer import IOBuffer
from spinnman.messages.scp.impl.scp_read_memory_request \
    import SCPReadMemoryRequest
from spinnman.processes.abstract_multi_connection_process \
    import AbstractMultiConnectionProcess
from spinnman import constants


class ReadIOBufProcess(AbstractMultiConnectionProcess):
    """ A process for reading memory
    """

    def __init__(self, machine, connections, next_connection_selector=None):
        AbstractMultiConnectionProcess.__init__(
            self, connections, next_connection_selector)
        self._connections = connections
        self._machine = machine

        # A list of next reads that need to be done as a result of the first
        # read = list of (x, y, p, n, next_address)
        self._next_reads = list()

    def handle_first_iobuf_response(self, x, y, p, n, base_address, response):

        # Unpack the iobuf header
        next_address = struct.unpack_from(
            "<I", response.data, response.offset)[0]

        # If there is another IOBuf buffer, read this next
        if next_address != 0:
            self._next_reads.append((x, y, p, n + 1, next_address))

    def reset_iobuf(self, chip_info, core_subsets):
        cpu_info_process = GetCPUInfoProcess(self._machine, self._connections)
        cpu_information = cpu_info_process.get_cpu_info(chip_info,
                                                        core_subsets)

        # Kick-start the reading of the IOBufs
        for cpu_info in cpu_information:
            if cpu_info.iobuf_address != 0:
                self._next_reads.append((
                    cpu_info.x, cpu_info.y, cpu_info.p, 0,
                    cpu_info.iobuf_address))

        # Run rounds of the process until reading is complete
        while len(self._next_reads) > 0:

            # Process the next iobuf reads needed
            while len(self._next_reads) > 0:
                (x, y, p, n, next_address) = self._next_reads.pop()
                self._send_request(
                    SCPReadMemoryRequest(x, y, next_address, 4),
                    functools.partial(self.handle_first_iobuf_response,
                                      x, y, p, n, next_address))

            # Finish this round
            self._finish()

        self.check_for_error()
        for core_subset in core_subsets:
            x = core_subset.x
            y = core_subset.y
            for p in core_subset.processor_ids:
                iobufs = self._iobuf[(x, y, p)]
                iobuf = ""
                for item in iobufs.itervalues():
                    iobuf += item.decode("ascii")

                yield IOBuffer(x, y, p, iobuf)
