from spinnman.model.cpu_info import CPUInfo
from spinnman import constants
from spinnman.messages.spinnaker_boot._system_variables.\
    _system_variable_boot_values import SystemVariableDefinition
from spinnman.utilities import utility_functions
from spinnman.messages.scp.impl.scp_read_memory_request \
    import SCPReadMemoryRequest
from spinnman.processes.abstract_multi_connection_process \
    import AbstractMultiConnectionProcess

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
                base_address = utility_functions.get_vcpu_address(p)
                self._send_request(SCPReadMemoryRequest(
                    x, y, base_address, constants.CPU_INFO_BYTES),
                    functools.partial(self.handle_response, x, y, p))
        self._finish()
        self.check_for_error()

        return self._cpu_info
