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
from spinnman.messages.scp.impl import GetVersion
from spinnman.messages.scp.enums import SCPCommand


class TestSCPVersionRequest(unittest.TestCase):

    def setUp(self):
        unittest_setup()

    def test_new_version_request(self):
        ver_request = GetVersion(0, 1, 2)
        self.assertEqual(ver_request.scp_request_header.command,
                         SCPCommand.CMD_VER)
        self.assertEqual(ver_request.sdp_header.destination_chip_x, 0)
        self.assertEqual(ver_request.sdp_header.destination_chip_y, 1)
        self.assertEqual(ver_request.sdp_header.destination_cpu, 2)


if __name__ == '__main__':
    unittest.main()
