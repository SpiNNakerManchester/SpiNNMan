# Copyright (c) 2017-2019 The University of Manchester
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

import unittest
import struct
from spinn_machine import virtual_machine
from spinnman.config_setup import unittest_setup
from spinnman.data.spinnman_data_writer import SpiNNManDataWriter
from spinnman.transceiver import Transceiver
from spinnman import constants
from spinnman.messages.spinnaker_boot.system_variable_boot_values import (
    SystemVariableDefinition)
from spinnman.connections.udp_packet_connections import (
    BootConnection, EIEIOConnection, SCAMPConnection)
import spinnman.transceiver as transceiver
from board_test_configuration import BoardTestConfiguration

board_config = BoardTestConfiguration()
ver = 5  # Guess?


class MockWriteTransceiver(Transceiver):

    def __init__(
            self, version, connections=None):
        super().__init__(version, connections=connections)
        self.written_memory = list()

    def get_machine_details(self):
        return virtual_machine(2, 2)

    def _update_machine(self):
        self._machine = self.get_machine_details()

    def write_memory(
            self, x, y, base_address, data, n_bytes=None, offset=0,
            cpu=0, is_filename=False):
        print("Doing write to", x, y)
        self.written_memory.append(
            (x, y, base_address, data, n_bytes, offset, cpu, is_filename))

    def close(self):
        pass


class TestTransceiver(unittest.TestCase):

    def setUp(self):
        unittest_setup()

    def test_create_new_transceiver_to_board(self):
        board_config.set_up_remote_board()
        connections = list()
        connections.append(SCAMPConnection(
            remote_host=board_config.remotehost))
        trans = transceiver.Transceiver(ver, connections=connections)
        trans.close()

    def test_create_new_transceiver_one_connection(self):
        board_config.set_up_remote_board()
        connections = set()
        connections.add(SCAMPConnection(
            remote_host=board_config.remotehost))
        with transceiver.Transceiver(ver, connections=connections) as trans:
            assert trans.get_connections() == connections

    def test_create_new_transceiver_from_list_connections(self):
        board_config.set_up_remote_board()
        connections = list()
        connections.append(SCAMPConnection(
            remote_host=board_config.remotehost))
        board_config.set_up_local_virtual_board()
        connections.append(BootConnection(
            remote_host=board_config.remotehost))
        with transceiver.Transceiver(ver, connections=connections) as trans:
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
        with transceiver.Transceiver(ver, connections=connections) as trans:
            SpiNNManDataWriter.mock().set_machine(trans.get_machine_details())
            if board_config.board_version in (2, 3):
                assert trans.get_machine_dimensions().width == 2
                assert trans.get_machine_dimensions().height == 2
            elif board_config.board_version in (4, 5):
                assert trans.get_machine_dimensions().width == 8
                assert trans.get_machine_dimensions().height == 8
            else:
                size = trans.get_machine_dimensions()
                print(f"Unknown board with size {size.width} x {size.height}")

            assert trans.is_connected()
            print(trans.get_scamp_version())
            print(trans.get_cpu_information())

    def test_boot_board(self):
        board_config.set_up_remote_board()
        with transceiver.create_transceiver_from_hostname(
                board_config.remotehost, board_config.board_version) as trans:
            # self.assertFalse(trans.is_connected())
            trans.boot_board()

    def test_set_watch_dog(self):
        connections = []
        connections.append(SCAMPConnection(remote_host=None))
        tx = MockWriteTransceiver(version=5, connections=connections)
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
