import unittest
from spinnman.connections.udp_packet_connections.udp_boot_connection import \
    UDPBootConnection


class MyTestCase(unittest.TestCase):
    def test_something(self):
        udp_connect = UDPBootConnection()
        self.assertIsNotNone(udp_connect)


if __name__ == '__main__':
    unittest.main()
