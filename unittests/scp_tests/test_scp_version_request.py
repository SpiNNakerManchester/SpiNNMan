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
from spinnman.messages.scp.impl import GetVersion
from spinnman.messages.scp.enums import SCPCommand


class TestSCPVersionRequest(unittest.TestCase):

    def setUp(self) -> None:
        unittest_setup()

    def test_new_version_request(self) -> None:
        ver_request = GetVersion(0, 1, 2)
        self.assertEqual(ver_request.scp_request_header.command,
                         SCPCommand.CMD_VER)
        self.assertEqual(ver_request.sdp_header.destination_chip_x, 0)
        self.assertEqual(ver_request.sdp_header.destination_chip_y, 1)
        self.assertEqual(ver_request.sdp_header.destination_cpu, 2)


if __name__ == '__main__':
    unittest.main()
