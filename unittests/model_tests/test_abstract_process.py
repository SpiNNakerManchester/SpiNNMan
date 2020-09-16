from spinnman.processes.abstract_single_connection_process import (
    AbstractSingleConnectionProcess)
from spinnman.messages.scp.impl import ReadMemory
from spinnman.connections.udp_packet_connections import SCAMPConnection
from spinnman.exceptions import SpinnmanTimeoutException
from spinnman.processes import RoundRobinConnectionSelector
import pytest


class MockProcess(AbstractSingleConnectionProcess):

    def test(self):
        self._send_request(ReadMemory(0, 0, 0, 4))
        self._finish()
        self.check_for_error(print_exception=True)


class MockConnection(SCAMPConnection):

    def send(self, data):
        pass

    def receive_scp_response(self, timeout=1.0):
        raise SpinnmanTimeoutException("Test", timeout)


def test_error_print():
    connection = MockConnection(0, 0)
    process = MockProcess(RoundRobinConnectionSelector([connection]))
    with pytest.raises(SpinnmanTimeoutException):
        process.test()
