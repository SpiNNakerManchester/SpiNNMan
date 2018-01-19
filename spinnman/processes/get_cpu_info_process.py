from spinnman.model import CPUInfo
from spinnman.constants import CPU_INFO_BYTES
from spinnman.utilities.utility_functions import get_vcpu_address
from spinnman.messages.scp.impl import ReadMemory
from .abstract_multi_connection_process import AbstractMultiConnectionProcess

import functools


class GetCPUInfoProcess(AbstractMultiConnectionProcess):
    __slots__ = [
        "_cpu_info"]

    def __init__(self, connection_selector):
        super(GetCPUInfoProcess, self).__init__(connection_selector)
        self._cpu_info = list()

    def handle_response(self, x, y, p, response):
        self._cpu_info.append(CPUInfo(x, y, p, response.data, response.offset))

    def get_cpu_info(self, core_subsets):
        for core_subset in core_subsets:
            x = core_subset.x
            y = core_subset.y

            for p in core_subset.processor_ids:
                self._send_request(
                    ReadMemory(x, y, get_vcpu_address(p), CPU_INFO_BYTES),
                    functools.partial(self.handle_response, x, y, p))
        self._finish()
        self.check_for_error()

        return self._cpu_info
