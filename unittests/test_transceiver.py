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
from spinnman.config_setup import unittest_setup
from spinnman.data.spinnman_data_writer import SpiNNManDataWriter
from spinnman.transceiver import (
    create_transceiver_from_hostname, MockableTransceiver)
from spinnman.transceiver.watchdog_setter import WatchdogSetter
from spinnman.transceiver.version5Transceiver import Version5Transceiver
from spinnman import constants
from spinnman.messages.spinnaker_boot.system_variable_boot_values import (
    SystemVariableDefinition)
from spinnman.connections.udp_packet_connections import (
    BootConnection, SCAMPConnection)
import spinnman.extended.extended_transceiver as extended
from spinnman.board_test_configuration import BoardTestConfiguration

board_config = BoardTestConfiguration()
ver = 5  # Guess?


class MockExtendedTransceiver(MockableTransceiver, WatchdogSetter):
    pass


class TestTransceiver(unittest.TestCase):

    def setUp(self):
        unittest_setup()
        set_config("Machine", "version", 5)

    def test_create_new_transceiver_to_board(self):
        board_config.set_up_remote_board()
        connections = list()
        connections.append(SCAMPConnection(
            remote_host=board_config.remotehost))
        trans = Version5Transceiver(ver, connections=connections)
        trans.close()

    def test_create_new_transceiver_one_connection(self):
        board_config.set_up_remote_board()
        connections = set()
        connections.add(SCAMPConnection(
            remote_host=board_config.remotehost))
        with extended.ExtendedTransceiver(
                ver, connections=connections) as trans:
            assert trans.get_connections() == connections

    def test_create_new_transceiver_from_list_connections(self):
        board_config.set_up_remote_board()
        connections = list()
        connections.append(SCAMPConnection(
            remote_host=board_config.remotehost))
        board_config.set_up_local_virtual_board()
        connections.append(BootConnection(
            remote_host=board_config.remotehost))
        with Version5Transceiver(ver, connections=connections) as trans:
            instantiated_connections = trans.get_connections()

            for connection in connections:
                assert connection in instantiated_connections
            # assert trans.get_connections() == connections

    def test_retrieving_machine_details(self):
        board_config.set_up_remote_board()
        connections = list()
        connections.append(SCAMPConnection(
            remote_host=board_config.remotehost))
        board_config.set_up_local_virtual_board()
        connections.append(BootConnection(
            remote_host=board_config.remotehost))
        with Version5Transceiver(ver, connections=connections) as trans:
            SpiNNManDataWriter.mock().set_machine(trans.get_machine_details())
            if board_config.board_version in (2, 3):
                assert trans._get_machine_dimensions().width == 2
                assert trans._get_machine_dimensions().height == 2
            elif board_config.board_version in (4, 5):
                assert trans._get_machine_dimensions().width == 8
                assert trans._get_machine_dimensions().height == 8
            else:
                size = trans._get_machine_dimensions()
                print(f"Unknown board with size {size.width} x {size.height}")

            assert trans.is_connected()
            print(trans._get_scamp_version())
            print(trans.get_cpu_infos())

    def test_boot_board(self):
        board_config.set_up_remote_board()
        with create_transceiver_from_hostname(
                board_config.remotehost, board_config.board_version) as trans:
            # self.assertFalse(trans.is_connected())
            trans._boot_board()

    def test_set_watch_dog(self):
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
