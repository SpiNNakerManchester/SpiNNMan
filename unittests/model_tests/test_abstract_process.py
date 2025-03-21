# Copyright (c) 2020 The University of Manchester
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Optional
from typing_extensions import Never
from spinn_utilities.config_holder import set_config
from spinn_utilities.overrides import overrides
from spinn_machine.version.version_strings import VersionStrings
from spinnman.processes.abstract_multi_connection_process import (
    AbstractMultiConnectionProcess)
from spinnman.messages.scp.impl import ReadMemory
from spinnman.config_setup import unittest_setup
from spinnman.connections.udp_packet_connections import SCAMPConnection
from spinnman.exceptions import (
    SpinnmanTimeoutException, SpinnmanGenericProcessException)
from spinnman.processes import RoundRobinConnectionSelector
import pytest


class MockProcess(AbstractMultiConnectionProcess):
    def test(self) -> None:
        with self._collect_responses(print_exception=True):
            self._send_request(ReadMemory((0, 0, 0), 0, 4))


class MockConnection(SCAMPConnection):

    @overrides(SCAMPConnection.send)
    def send(self, data: bytes) -> None:
        pass

    @overrides(SCAMPConnection.receive_scp_response)
    def receive_scp_response(self, timeout: Optional[float] = 1.0) -> Never:
        raise SpinnmanTimeoutException("Test", timeout)


def test_error_print() -> None:
    unittest_setup()
    set_config("Machine", "versions", VersionStrings.ANY.text)
    connection = MockConnection(0, 0)
    process = MockProcess(RoundRobinConnectionSelector([connection]))
    with pytest.raises(SpinnmanGenericProcessException):
        process.test()
