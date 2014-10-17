import unittest
import spinnman.transceiver as transceiver
from spinnman.connections.udp_connection import UDPConnection
import time
class TestTransceiver(unittest.TestCase):

    def test_create_new_default_transceiver(self):
        trans = transceiver.Transceiver(discover=False)

        self.assertEqual(trans.get_connections(), [])
        trans.close()

    def test_create_new_default_transceiver_discover(self):
        trans = transceiver.Transceiver(discover=True)

        self.assertNotEqual(trans.get_connections(), [])
        trans.close()

    def test_create_new_transceiver_one_connection_discovery(self):
        self.set_up_remote_board()
        connections = list()
        connections.append(UDPConnection(self.localhost,self.localport,self.remotehost,self.remoteport))
        trans = transceiver.Transceiver(connections)

        self.assertEqual(trans.get_connections(), connections)
        trans.close()

    def test_create_new_transceiver_from_list_connections_discovery(self):
        self.set_up_remote_board()
        connections = list()
        connections.append(UDPConnection(self.localhost,self.localport,self.remotehost,self.remoteport))
        self.set_up_local_virtual_board()
        connections.append(UDPConnection(self.localhost,self.localport,self.remotehost,self.remoteport))
        trans = transceiver.Transceiver(connections)

        self.assertEqual(trans.get_connections(), connections)
        trans.close()

    def test_create_new_transceiver_one_connection_no_discovery(self):
        self.set_up_remote_board()
        connections = list()
        connections.append(UDPConnection(self.localhost,self.localport,self.remotehost,self.remoteport))
        trans = transceiver.Transceiver(connections,False)
        self.assertEqual(trans.get_connections(), connections)
        trans.close()

    def test_create_new_transceiver_from_list_connections_no_discovery(self):
        self.set_up_remote_board()
        connections = list()
        connections.append(UDPConnection(self.localhost,self.localport,self.remotehost,self.remoteport))
        self.set_up_local_virtual_board()
        connections.append(UDPConnection(self.localhost,self.localport,self.remotehost,self.remoteport))
        trans = transceiver.Transceiver(connections, False)

        self.assertEqual(trans.get_connections(), connections)
        trans.close()

    def test_retrieving_machine_details(self):
        self.set_up_remote_board()
        connections = list()
        connections.append(UDPConnection(self.localhost,self.localport,self.remotehost,self.remoteport))
        trans = transceiver.Transceiver(connections,False)

        self.assertEqual(trans.get_machine_dimensions().x_max,1)
        self.assertEqual(trans.get_machine_dimensions().y_max,1)
        self.assertTrue(trans.is_connected())
        print trans.get_scamp_version()
        print trans.get_cpu_information()


        trans.close()

    def test_boot_board(self):
        self.set_up_remote_board()
        trans = transceiver.create_transceiver_from_hostname(self.remotehost)
        #self.assertFalse(trans.is_connected())
        trans.boot_board(3)
        trans.close()

    def set_up_local_virtual_board(self):
        self.localhost = "127.0.0.1"
        self.localport = 54321
        self.remotehost = "127.0.0.1"
        self.remoteport = 17893

    def set_up_remote_board(self):
        self.localhost = "192.168.240.254"
        self.localport = 54321
        self.remotehost = "192.168.240.253"
        self.remoteport = 17893


if __name__ == '__main__':
    unittest.main()
