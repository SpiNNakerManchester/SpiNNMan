# Copyright (c) 2014 The University of Manchester
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

import unittest
import struct
from spinn_utilities.overrides import overrides
from spinn_utilities.config_holder import set_config
from spinn_machine import virtual_machine
from spinnman.config_setup import unittest_setup
from spinnman.data import SpiNNManDataView
from spinnman.data.spinnman_data_writer import SpiNNManDataWriter
from spinnman.extended.extended_transceiver import ExtendedTransceiver
from spinnman.transceiver import Transceiver
from spinnman import constants
from spinnman.messages.spinnaker_boot.system_variable_boot_values import (
    SystemVariableDefinition)
from spinnman.connections.udp_packet_connections import (
    BootConnection, SCAMPConnection)
import spinnman.transceiver as transceiver
import spinnman.extended.extended_transceiver as extended
from spinnman.board_test_configuration import BoardTestConfiguration

ver = 5  # Guess?


class MockWriteTransceiver(Transceiver):

    def __init__(
            self, version, connections=None):
        super().__init__(version, connections=connections)
        self.written_memory = list()

    def get_machine_details(self):
        version = SpiNNManDataView.get_machine_version()
        width, height = version.board_shape
        return virtual_machine(width, height)

    def _update_machine(self):
        self._machine = self.get_machine_details()

    @overrides(Transceiver.write_memory)
    def write_memory(
            self, x, y, base_address, data, *,
            n_bytes=None, offset=0, cpu=0, get_sum=False):
        print("Doing write to", x, y)
        self.written_memory.append(
            (x, y, base_address, data, n_bytes, offset, cpu,
             isinstance(data, str)))
        return len(data), 0

    def close(self):
        pass

    def _ensure_board_is_ready(self, n_retries=5, extra_boot_values=None):
        pass


class MockExtendedTransceiver(MockWriteTransceiver, ExtendedTransceiver):
    pass


class TestTransceiver(unittest.TestCase):

    def setUp(self):
        unittest_setup()
        self.board_config = BoardTestConfiguration()

    def test_create_new_transceiver_to_board(self):
        self.board_config.set_up_remote_board()
        connections = [
            SCAMPConnection(remote_host=self.board_config.remotehost)]
        trans = transceiver.Transceiver(ver, connections=connections)
        trans.close()

    def test_create_new_transceiver_one_connection(self):
        self.board_config.set_up_remote_board()
        connections = {
            SCAMPConnection(remote_host=self.board_config.remotehost)}
        with extended.ExtendedTransceiver(
                ver, connections=connections) as trans:
            assert trans._all_connections == connections

    def test_create_new_transceiver_from_list_connections(self):
        self.board_config.set_up_remote_board()
        connections = list()
        connections.append(SCAMPConnection(
            remote_host=self.board_config.remotehost))
        connections.append(BootConnection(remote_host="127.0.0.1"))
        with transceiver.Transceiver(ver, connections=connections) as trans:
            instantiated_connections = trans._all_connections

            for connection in connections:
                assert connection in instantiated_connections
            # assert trans.get_connections() == connections

    def test_retrieving_machine_details(self):
        self.board_config.set_up_remote_board()
        connections = list()
        connections.append(SCAMPConnection(
            remote_host=self.board_config.remotehost))
        connections.append(BootConnection(remote_host="127.0.0.1"))
        with transceiver.Transceiver(ver, connections=connections) as trans:
            SpiNNManDataWriter.mock().set_machine(trans.get_machine_details())
            if self.board_config.board_version in (2, 3):
                assert trans._get_machine_dimensions().width == 2
                assert trans._get_machine_dimensions().height == 2
            elif self.board_config.board_version in (4, 5):
                assert trans._get_machine_dimensions().width == 8
                assert trans._get_machine_dimensions().height == 8
            else:
                size = trans._get_machine_dimensions()
                print(f"Unknown board with size {size.width} x {size.height}")

            assert any(c.is_connected() for c in trans._scamp_connections)
            print(trans._get_scamp_version())
            print(trans.get_cpu_infos())

    def test_boot_board(self):
        self.board_config.set_up_remote_board()
        with transceiver.create_transceiver_from_hostname(
                self.board_config.remotehost,
                self.board_config.board_version) as trans:
            # self.assertFalse(trans.is_connected(        unittest_setup()))
            trans._boot_board()

    def test_set_watch_dog(self):
        set_config("Machine", "version", 5)
        connections = []
        connections.append(SCAMPConnection(remote_host=None))
        tx = MockExtendedTransceiver(version=5, connections=connections)
        SpiNNManDataWriter.mock().set_machine(tx.get_machine_details())
        # All chips
        tx.set_watch_dog(True)
        tx.set_watch_dog(False)
        tx.set_watch_dog(5)

        # The expected write values for the watch dog
        expected_writes = (
            SystemVariableDefinition.software_watchdog_count.default, 0, 5)

        # Check the values that were "written" for set_watch_dog,
        # which should be one per chip
        written_memory = tx.written_memory
        write_item = 0
        for write in range(3):
            for x, y in tx.get_machine_details().chip_coordinates:
                assert written_memory[write_item][0] == x
                assert written_memory[write_item][1] == y
                assert written_memory[write_item][2] == (
                    constants.SYSTEM_VARIABLE_BASE_ADDRESS +
                    SystemVariableDefinition.software_watchdog_count.offset)
                expected_data = struct.pack("B", expected_writes[write])
                assert written_memory[write_item][3] == expected_data
                write_item += 1


if __name__ == '__main__':
    unittest.main()
