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
from spinnman.config_setup import unittest_setup
from spinnman.messages.scp import SCPRequestHeader
from spinnman.messages.scp.enums import SCPCommand
from spinnman.messages.scp.impl import GetVersion, ReadLink, ReadMemory


class TestSCPMessageAssembly(unittest.TestCase):

    def setUp(self):
        unittest_setup()

    def test_create_new_scp_header(self):
        header = SCPRequestHeader(SCPCommand.CMD_VER)

        self.assertEqual(header.command, SCPCommand.CMD_VER)
        self.assertEqual(header.sequence, 0)

    def test_create_new_ver_scp_pkt(self):
        scp = GetVersion(0, 0, 0)
        self.assertEqual(scp.argument_1, None)
        self.assertEqual(scp.argument_2, None)
        self.assertEqual(scp.argument_3, None)
        self.assertEqual(scp.data, None)

    def test_create_new_link_scp_pkt(self):
        scp = ReadLink(0, 0, 0, 0, 256)
        self.assertEqual(scp.argument_1, 0)
        self.assertEqual(scp.argument_2, 256)
        self.assertEqual(scp.argument_3, 0)
        self.assertEqual(scp.data, None)

    def test_create_new_memory_scp_pkt(self):
        scp = ReadMemory(0, 0, 0, 256)
        self.assertEqual(scp.argument_1, 0)
        self.assertEqual(scp.argument_2, 256)
        self.assertEqual(scp.argument_3, 2)
        self.assertEqual(scp.data, None)


if __name__ == '__main__':
    unittest.main()
