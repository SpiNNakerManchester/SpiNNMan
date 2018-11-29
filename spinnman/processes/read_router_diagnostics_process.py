import struct
from spinnman.messages.scp.impl import ReadMemory
from spinnman.model import RouterDiagnostics
from .abstract_multi_connection_process import AbstractMultiConnectionProcess

_N_REGISTERS = 16
_ONE_WORD = struct.Struct("<I")


class ReadRouterDiagnosticsProcess(AbstractMultiConnectionProcess):
    """ A process for reading the diagnostic data block from a SpiNNaker\
        router.
    """
    __slots__ = [
        "_control_register",
        "_error_status",
        "_register_values"]

    def __init__(self, connection_selector):
        super(ReadRouterDiagnosticsProcess, self).__init__(connection_selector)
        self._control_register = None
        self._error_status = None
        self._register_values = [0] * _N_REGISTERS

    def handle_control_register_response(self, response):
        self._control_register = _ONE_WORD.unpack_from(
            response.data, response.offset)[0]

    def handle_error_status_response(self, response):
        self._error_status = _ONE_WORD.unpack_from(
            response.data, response.offset)[0]

    def handle_register_response(self, response):
        for register in range(_N_REGISTERS):
            self._register_values[register] = _ONE_WORD.unpack_from(
                response.data, response.offset + (register * 4))[0]

    def get_router_diagnostics(self, x, y):
        self._send_request(ReadMemory(x, y, 0xe1000000, 4),
                           self.handle_control_register_response)
        self._send_request(ReadMemory(x, y, 0xe1000014, 4),
                           self.handle_error_status_response)
        self._send_request(ReadMemory(x, y, 0xe1000300, 16 * 4),
                           self.handle_register_response)
        self._finish()
        self.check_for_error()

        return RouterDiagnostics(self._control_register, self._error_status,
                                 self._register_values)
