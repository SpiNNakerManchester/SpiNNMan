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
from spinnman.config_setup import unittest_setup
from spinnman.messages.scp import SCPRequestHeader
from spinnman.messages.scp.enums import SCPCommand
from spinnman.messages.scp.impl import GetVersion, ReadLink, ReadMemory


class TestSCPMessageAssembly(unittest.TestCase):

    def setUp(self) -> None:
        unittest_setup()

    def test_create_new_scp_header(self) -> None:
        header = SCPRequestHeader(SCPCommand.CMD_VER)

        self.assertEqual(header.command, SCPCommand.CMD_VER)
        self.assertEqual(header.sequence, 0)

    def test_create_new_ver_scp_pkt(self) -> None:
        scp = GetVersion(0, 0, 0)
        self.assertEqual(scp.argument_1, None)
        self.assertEqual(scp.argument_2, None)
        self.assertEqual(scp.argument_3, None)
        self.assertEqual(scp.data, None)

    def test_create_new_link_scp_pkt(self) -> None:
        scp = ReadLink((0, 0, 0), 0, 0, 256)
        self.assertEqual(scp.argument_1, 0)
        self.assertEqual(scp.argument_2, 256)
        self.assertEqual(scp.argument_3, 0)
        self.assertEqual(scp.data, None)

    def test_create_new_memory_scp_pkt(self) -> None:
        scp = ReadMemory((0, 0, 0), 0, 256)
        self.assertEqual(scp.argument_1, 0)
        self.assertEqual(scp.argument_2, 256)
        self.assertEqual(scp.argument_3, 2)
        self.assertEqual(scp.data, None)


if __name__ == '__main__':
    unittest.main()
