# Copyright (c) 2017-2019 The University of Manchester
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import unittest
from spinn_machine.tags import IPTag
from board_test_configuration import BoardTestConfiguration
from spinnman.config_setup import unittest_setup

board_config = BoardTestConfiguration()


class TestIptag(unittest.TestCase):

    def setUp(self):
        unittest_setup()

    def test_new_iptag(self):
        board_config.set_up_remote_board()
        ip = "8.8.8.8"
        port = 1337
        tag = 255
        board_address = board_config.remotehost
        iptag = IPTag(board_address, 0, 0, tag, ip, port)
        self.assertEqual(ip, iptag.ip_address)
        self.assertEqual(port, iptag.port)
        self.assertEqual(tag, iptag.tag)


if __name__ == '__main__':
    unittest.main()
