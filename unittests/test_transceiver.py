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
from spinn_machine import virtual_machine
from spinnman.config_setup import unittest_setup
from spinnman.data.spinnman_data_writer import SpiNNManDataWriter
from spinnman.transceiver import Transceiver
from spinnman import constants
from spinnman.messages.spinnaker_boot.system_variable_boot_values import (
    SystemVariableDefinition)
from spinnman.connections.udp_packet_connections import (
    BootConnection, SCAMPConnection)
import spinnman.transceiver as transceiver
from spinnman.board_test_configuration import BoardTestConfiguration

board_config = BoardTestConfiguration()
ver = 5  # Guess?


class MockWriteTransceiver(Transceiver):

    def __init__(
            self, version, connections=None):
        super().__init__(version, connections=connections)
        self.written_memory = list()

    def get_machine_details(self):
        return virtual_machine(8, 8)

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
        set_config("Machine", "version", 5)

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

    def test_create_new_transceiver_from_list_connections(self):
        board_config.set_up_remote_board()
        connections = list()
        connections.append(SCAMPConnection(
            remote_host=board_config.remotehost))
        board_config.set_up_local_virtual_board()
        connections.append(BootConnection(
            remote_host=board_config.remotehost))

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
        with transceiver.create_transceiver_from_hostname(
                board_config.remotehost, board_config.board_version) as trans:
            # self.assertFalse(trans.is_connected())
            trans._boot_board()


if __name__ == '__main__':
    unittest.main()
