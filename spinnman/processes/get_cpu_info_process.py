from spinnman.model import CPUInfo
from spinnman.constants import CPU_INFO_BYTES
from spinnman.messages.spinnaker_boot import SystemVariableDefinition
from spinnman.utilities.utility_functions import get_vcpu_address
from spinnman.messages.scp.impl import ReadMemory
from .abstract_multi_connection_process import AbstractMultiConnectionProcess

import functools
import struct


VCPU = SystemVariableDefinition.cpu_information_base_address


class GetCPUInfoProcess(AbstractMultiConnectionProcess):
    def __init__(self, connection_selector):
        AbstractMultiConnectionProcess.__init__(self, connection_selector)
        self._vcpu_offsets = None
        self._cpu_info = list()

    def handle_read_vcpu_offset(self, x, y, response):
        offset = struct.unpack_from(
            VCPU.data_type.struct_code, response.data, response.offset)[0]
        self._vcpu_offsets[x, y] = offset

    def handle_response(self, x, y, p, response):
        self._cpu_info.append(CPUInfo(x, y, p, response.data, response.offset))

    def get_cpu_info(self, core_subsets):
        for core_subset in core_subsets:
            x = core_subset.x
            y = core_subset.y

            for p in core_subset.processor_ids:
                self._send_request(ReadMemory(
                    x, y, get_vcpu_address(p), CPU_INFO_BYTES),
                    functools.partial(self.handle_response, x, y, p))
        self._finish()
        self.check_for_error()

        return self._cpu_info
