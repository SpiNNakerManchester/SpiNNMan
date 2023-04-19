# Copyright (c) 2014 The University of Manchester
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
from spinn_machine.tags import IPTag
from spinnman.board_test_configuration import BoardTestConfiguration
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
