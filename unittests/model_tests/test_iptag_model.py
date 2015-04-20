import unittest

from spinn_machine.tags.iptag import IPTag
from spinnman.board_test_configuration import BoardTestConfiguration

board_config = BoardTestConfiguration()


class TestIptag(unittest.TestCase):
    def test_new_iptag(self):
        board_config.set_up_remote_board()
        ip = "8.8.8.8"
        port = 1337
        tag = 255
        board_address = board_config.remotehost
        iptag = IPTag(board_address, tag, ip, port)
        self.assertEqual(ip, iptag.ip_address)
        self.assertEqual(port, iptag.port)
        self.assertEqual(tag, iptag.tag)


if __name__ == '__main__':
    unittest.main()
