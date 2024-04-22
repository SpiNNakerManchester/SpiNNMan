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
from spinn_utilities.config_holder import set_config
from spinn_machine.version.version_strings import VersionStrings
from spinnman.config_setup import unittest_setup
from spinnman.data import SpiNNManDataView
from spinnman.data.spinnman_data_writer import SpiNNManDataWriter
from spinnman.transceiver import (
    create_transceiver_from_connections, create_transceiver_from_hostname,
    MockableTransceiver)
from spinnman.extended.extended_transceiver import ExtendedTransceiver
from spinnman import constants
from spinnman.messages.spinnaker_boot.system_variable_boot_values import (
    SystemVariableDefinition)
from spinnman.connections.udp_packet_connections import SCAMPConnection
from spinnman.board_test_configuration import BoardTestConfiguration


class MockExtendedTransceiver(MockableTransceiver, ExtendedTransceiver):
    pass

    def _where_is_xy(self, x: int, y: int) -> None:
        return None

    def scamp_connection_selector(self):
        raise NotImplementedError


class TestTransceiver(unittest.TestCase):

    def setUp(self):
        unittest_setup()
        self.board_config = BoardTestConfiguration()

    def test_create_new_transceiver_to_board(self):
        self.board_config.set_up_remote_board()
        connections = list()
        connections.append(SCAMPConnection(
            remote_host=self.board_config.remotehost))
        trans = create_transceiver_from_connections(connections=connections)
        trans.get_connections() == connections
        trans.close()

    def test_create_new_transceiver_one_connection(self):
        self.board_config.set_up_remote_board()
        connections = set()
        connections.add(SCAMPConnection(
            remote_host=self.board_config.remotehost))
        trans = create_transceiver_from_connections(connections=connections)
        self.assertSetEqual(connections, trans.get_connections())
        trans.close()

    def test_retrieving_machine_details(self):
        self.board_config.set_up_remote_board()
        trans = create_transceiver_from_hostname(self.board_config.remotehost)
        SpiNNManDataWriter.mock().set_machine(trans.get_machine_details())
        version = SpiNNManDataView.get_machine_version()
        self.assertEqual(
            version.board_shape,
            (trans._get_machine_dimensions().width,
             trans._get_machine_dimensions().height))

        assert any(c.is_connected() for c in trans._scamp_connections)
        print(trans._get_scamp_version())
        print(trans.get_cpu_infos())

    def test_boot_board(self):
        self.board_config.set_up_remote_board()
        trans = create_transceiver_from_hostname(self.board_config.remotehost)
        trans._boot_board()

    def test_set_watch_dog(self):
        set_config("Machine", "versions", VersionStrings.ANY.text)
        connections = []
        connections.append(SCAMPConnection(remote_host=None))
        tx = MockExtendedTransceiver()
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
