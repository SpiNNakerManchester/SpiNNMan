import unittest
from board_test_configuration import BoardTestConfiguration
from spinnman.connections.udp_packet_connections import BMPConnection

board_config = BoardTestConfiguration()


class TestBMPConnection(unittest.TestCase):

    def test_bmp_basics(self):
        board_config.set_up_remote_board()
        if board_config.bmp_names is None:
            raise unittest.SkipTest("no BMP available")
        cdata = board_config.bmp_names[0]
        connection = BMPConnection(connection_data=cdata)
        self.assertEqual(cdata.cabinet, connection.cabinet)
        self.assertEqual(cdata.frame, connection.frame)
        self.assertEqual(cdata.boards, connection.boards)
        self.assertEqual(0, connection.chip_x)
        self.assertEqual(0, connection.chip_y)
        self.assertNotEqual("", repr(connection))


if __name__ == '__main__':
    unittest.main()
