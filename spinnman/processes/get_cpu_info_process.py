from spinnman.processes.\
    multi_connection_process_most_direct_connection_selector \
    import MultiConnectionProcessMostDirectConnectionSelector
from spinnman.model.cpu_info import CPUInfo
from spinnman import constants
from spinnman.exceptions import SpinnmanInvalidParameterException
import functools
from spinnman.messages.scp.impl.scp_read_memory_request \
    import SCPReadMemoryRequest
from spinnman.processes.abstract_multi_connection_process \
    import AbstractMultiConnectionProcess


class GetCPUInfoProcess(AbstractMultiConnectionProcess):

    def __init__(self, machine, connections):
        AbstractMultiConnectionProcess.__init__(
            self, connections,
            MultiConnectionProcessMostDirectConnectionSelector(
                machine, connections))

        self._cpu_info = list()

    def handle_response(self, x, y, p, response):
        self._cpu_info.append(CPUInfo(x, y, p, response.data, response.offset))

    def get_cpu_info(self, chip_info, core_subsets):
        for core_subset in core_subsets:
            x = core_subset.x
            y = core_subset.y

            this_chip_info = chip_info[(x, y)]

            for p in core_subset.processor_ids:
                if p not in this_chip_info.virtual_core_ids:
                    raise SpinnmanInvalidParameterException(
                        "p", p, "Not a valid core on chip {}, {}".format(
                            x, y))
                base_address = (this_chip_info.cpu_information_base_address +
                                (constants.CPU_INFO_BYTES * p))
                self._send_request(SCPReadMemoryRequest(
                    x, y, base_address, constants.CPU_INFO_BYTES),
                    functools.partial(self.handle_response, x, y, p))
        self._finish()
        self.check_for_error()
        return self._cpu_info
