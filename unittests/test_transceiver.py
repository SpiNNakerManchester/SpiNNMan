import unittest
from spinnman.transceiver import Transceiver
from spinnman.connections.udp_packet_connections \
    import UDPBootConnection, UDPEIEIOConnection, UDPSCAMPConnection
import spinnman.transceiver as transceiver
from board_test_configuration import BoardTestConfiguration

board_config = BoardTestConfiguration()


ver = 5     # Guess?


class TestTransceiver(unittest.TestCase):

    def test_create_new_transceiver_to_board(self):
        board_config.set_up_remote_board()
        connections = list()
        connections.append(UDPSCAMPConnection(
            remote_host=board_config.remotehost))
        trans = transceiver.Transceiver(ver, connections=connections)
        trans.close()

    def test_create_new_transceiver_one_connection(self):
        board_config.set_up_remote_board()
        connections = set()
        connections.add(UDPSCAMPConnection(
            remote_host=board_config.remotehost))
        trans = transceiver.Transceiver(ver, connections=connections)

        assert trans.get_connections() == connections
        trans.close()

    def test_create_new_transceiver_from_list_connections(self):
        board_config.set_up_remote_board()
        connections = list()
        connections.append(UDPSCAMPConnection(
            remote_host=board_config.remotehost))
        board_config.set_up_local_virtual_board()
        connections.append(UDPBootConnection(
            remote_host=board_config.remotehost))
        trans = transceiver.Transceiver(ver, connections=connections)
        instantiated_connections = trans.get_connections()

        for connection in connections:
            assert connection in instantiated_connections
        # assert trans.get_connections() == connections
        trans.close()

    def test_retrieving_machine_details(self):
        board_config.set_up_remote_board()
        connections = list()
        connections.append(UDPSCAMPConnection(
            remote_host=board_config.remotehost))
        board_config.set_up_local_virtual_board()
        connections.append(UDPBootConnection(
            remote_host=board_config.remotehost))
        trans = transceiver.Transceiver(ver, connections=connections)

        if board_config.board_version == 3 or board_config.board_version == 2:
            assert trans.get_machine_dimensions().width == 2
            assert trans.get_machine_dimensions().height == 2
        elif (board_config.board_version == 5 or
                board_config.board_version == 4):
            assert trans.get_machine_dimensions().width == 8
            assert trans.get_machine_dimensions().height == 8
        else:
            size = trans.get_machine_dimensions()
            print "Unknown board with x size {0:d} and y size {1:d}".format(
                size.width, size.height)
        assert trans.is_connected()
        print trans.get_scamp_version()
        print trans.get_cpu_information()
        trans.close()

    def test_boot_board(self):
        board_config.set_up_remote_board()
        trans = transceiver.create_transceiver_from_hostname(
            board_config.remotehost, board_config.board_version)
        # self.assertFalse(trans.is_connected())
        trans.boot_board()
        trans.close()

    def test_listener_creation(self):
        # Tests the creation of listening sockets

        # Create board connections
        connections = []
        connections.append(UDPSCAMPConnection(
            remote_host=None))
        orig_connection = UDPEIEIOConnection()
        connections.append(orig_connection)

        # Create transceiver
        trnx = Transceiver(version=5, connections=connections)

        # Register a UDP listeners
        connection_1 = trnx.register_udp_listener(
            callback=None, connection_class=UDPEIEIOConnection)
        connection_2 = trnx.register_udp_listener(
            callback=None, connection_class=UDPEIEIOConnection)
        connection_3 = trnx.register_udp_listener(
            callback=None, connection_class=UDPEIEIOConnection,
            local_port=orig_connection.local_port)
        connection_4 = trnx.register_udp_listener(
            callback=None, connection_class=UDPEIEIOConnection,
            local_port=orig_connection.local_port + 1)

        assert connection_1 == orig_connection
        assert connection_2 == orig_connection
        assert connection_3 == orig_connection
        assert connection_4 != orig_connection


if __name__ == '__main__':
    unittest.main()
