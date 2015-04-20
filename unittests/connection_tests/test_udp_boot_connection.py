import unittest
from spinnman.connections.udp_packet_connections.udp_boot_connection import \
    UDPBootConnection


class MyTestCase(unittest.TestCase):
    def test_something(self):
        udp_connect = UDPBootConnection()


if __name__ == '__main__':
    unittest.main()
