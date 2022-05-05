# Copyright (c) 2020 The University of Manchester
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from spinnman.processes.abstract_single_connection_process import (
    AbstractSingleConnectionProcess)
from spinnman.messages.scp.impl import ReadMemory
from spinnman.config_setup import unittest_setup
from spinnman.connections.udp_packet_connections import SCAMPConnection
from spinnman.exceptions import (
    SpinnmanTimeoutException, SpinnmanGenericProcessException)
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
    unittest_setup()
    connection = MockConnection(0, 0)
    process = MockProcess(RoundRobinConnectionSelector([connection], None))
    with pytest.raises(SpinnmanGenericProcessException):
        process.test()
