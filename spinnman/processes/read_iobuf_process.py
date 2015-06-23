import functools
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
        self._iobuf = dict()

    def handle_first_iobuf_response(self, x, y, p, response):
        pass

    def handle_remaining_iobuf_response(self, x, y, p, response):
        pass

    def read_iobuf(self, chip_info, core_subsets):
        cpu_info_process = GetCPUInfoProcess(self._machine, self._connections)
        cpu_information = cpu_info_process.get_cpu_info(chip_info,
                                                        core_subsets)

        for cpu_info in cpu_information:
            this_chip_info = chip_info[(cpu_info.x, cpu_info.y)]
            iobuf_bytes = this_chip_info.iobuf_size
            base_address = cpu_info.iobuf_address

        self._finish()
        self.check_for_error()
        for core_subset in core_subsets:
            x = core_subset.x
            y = core_subset.y
            for p in core_subset.processor_ids:
                iobuf = self._iobuf[(x, y, p)]
                yield IOBuffer(x, y, p, iobuf)
