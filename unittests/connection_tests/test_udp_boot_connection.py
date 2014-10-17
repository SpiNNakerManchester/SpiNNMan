import unittest
from spinnman.connections.udp_boot_connection import UDPBootConnection

class MyTestCase(unittest.TestCase):
    def test_something(self):
        udp_connect = UDPBootConnection('192.168.240.254',54545,'192.168.240.253')



if __name__ == '__main__':
    unittest.main()
