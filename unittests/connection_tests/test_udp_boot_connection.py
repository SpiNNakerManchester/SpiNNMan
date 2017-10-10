import unittest
from spinnman.connections.udp_packet_connections import BootConnection


class MyTestCase(unittest.TestCase):
    def test_something(self):
        udp_connect = BootConnection()
        self.assertIsNotNone(udp_connect)


if __name__ == '__main__':
    unittest.main()
