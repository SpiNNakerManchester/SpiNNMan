__author__ = 'Petrut'

import unittest
import spinnman.connections.udp_connection as udp_conn

class TestUDPConnection(unittest.TestCase):
    def is_connected(self):
        return True

    def test_setup_new_udp_connection(self):
        #localhost = "127.0.0.1"
        #localport = "54321"
        #remotehost = "192.16.240.253"
        #remoteport = "12345"
        #connection = udp_conn.UDPConnection(localhost,localport, remotehost)
        pass

    def test_virtual_spinnaker_basic_message(self):
        localhost = "127.0.0.1"
        localport = "54321"
        remotehost = "127.0.0.1"
        #remoteport = "12345"
        connection = udp_conn.UDPConnection(localhost,localport, remotehost)

if __name__ == '__main__':
    unittest.main()
