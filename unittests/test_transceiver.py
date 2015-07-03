import unittest
from spinnman.connections.udp_packet_connections.udp_boot_connection import \
    UDPBootConnection
from spinnman.connections.udp_packet_connections.udp_scamp_connection \
    import UDPSCAMPConnection
from spinnman.exceptions import SpinnmanIOException
import spinnman.transceiver as transceiver
from board_test_configuration import BoardTestConfiguration

board_config = BoardTestConfiguration()


class TestTransceiver(unittest.TestCase):

    def test_create_new_default_transceiver(self):
        trans = transceiver.Transceiver()

        self.assertEqual(trans.get_connections(), [])
        trans.close()

    def test_create_new_transceiver_to_board(self):
        board_config.set_up_remote_board()
        connections = list()
        connections.append(UDPSCAMPConnection(
            board_config.localhost, board_config.localport,
            board_config.remotehost))
        trans = transceiver.Transceiver(connections)
        trans.close()

    def test_create_new_transceiver_one_connection(self):
        board_config.set_up_remote_board()
        connections = list()
        connections.append(UDPSCAMPConnection(
            board_config.localhost, board_config.localport,
            board_config.remotehost))
        trans = transceiver.Transceiver(connections)

        self.assertEqual(trans.get_connections(), connections)
        trans.close()

    def test_create_new_transceiver_from_list_connections(self):
        board_config.set_up_remote_board()
        connections = list()
        connections.append(UDPSCAMPConnection(
            local_host=board_config.localhost,
            remote_host=board_config.remotehost))
        board_config.set_up_local_virtual_board()
        connections.append(UDPBootConnection(
            local_host=board_config.localhost,
            remote_host=board_config.remotehost))
        trans = transceiver.Transceiver(connections)
        instantiated_connections = trans.get_connections(True)

        for connection in connections:
            self.assertTrue(connection in instantiated_connections)
        #self.assertEqual(trans.get_connections(), connections)
        trans.close()

    def test_retrieving_machine_details(self):
        board_config.set_up_remote_board()
        connections = list()
        connections.append(UDPSCAMPConnection(
            local_host=board_config.localhost,
            remote_host=board_config.remotehost))
        board_config.set_up_local_virtual_board()
        connections.append(UDPBootConnection(
            local_host=board_config.localhost,
            remote_host=board_config.remotehost))
        trans = transceiver.Transceiver(connections)

        if board_config.board_version == 3 or board_config.board_version == 2:
            self.assertEqual(trans.get_machine_dimensions().x_max, 1)
            self.assertEqual(trans.get_machine_dimensions().y_max, 1)
        elif board_config.board_version == 5 or board_config.board_version == 4:
            self.assertEqual(trans.get_machine_dimensions().x_max, 7)
            self.assertEqual(trans.get_machine_dimensions().y_max, 7)
        else:
            size = trans.get_machine_dimensions()
            print "Unknown board with x size {0:d} and y size {1:d}".format(
                size.x_max, size.y_max)
        self.assertTrue(trans.is_connected())
        print trans.get_scamp_version()
        print trans.get_cpu_information()
        trans.close()

    def test_boot_board(self):
        board_config.set_up_remote_board()
        trans = transceiver.create_transceiver_from_hostname(
            board_config.remotehost)
        #self.assertFalse(trans.is_connected())
        trans.boot_board(board_config.board_version)
        trans.close()


if __name__ == '__main__':
    unittest.main()
