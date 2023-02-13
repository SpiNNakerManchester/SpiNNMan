# Copyright (c) 2017-2023 The University of Manchester
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
from struct import pack
from spinnman.config_setup import unittest_setup
from spinnman.messages.scp.impl.get_version_response import GetVersionResponse
from spinnman.messages.scp.enums import SCPResult
from spinnman.messages.sdp import SDPFlag


class TestSCPVersionResponse(unittest.TestCase):

    def setUp(self):
        unittest_setup()

    def test_new_scp_version_response(self):
        GetVersionResponse()

    def test_read_scp_response(self):
        response = GetVersionResponse()
        # y
        # SCP Stuff
        rc = SCPResult.RC_OK.value
        seq = 105
        p2p_addr = 1024
        phys_cpu = 31
        virt_cpu = 14
        version = 234
        buffer = 250
        build_date = 103117
        ver_string = b"sark/spinnaker"

        # SDP stuff
        flags = SDPFlag.REPLY_NOT_EXPECTED.value
        tag = 5
        dest_port_cpu = 0x4f
        src_port_cpu = 0x6a
        dest_x = 0x11
        dest_y = 0xab
        src_x = 0x7
        src_y = 0x0
        data = pack(
            '<8BHHHBBHHI15s', flags, tag, dest_port_cpu, src_port_cpu, dest_y,
            dest_x, src_y, src_x, rc, seq, p2p_addr, phys_cpu, virt_cpu,
            version, buffer, build_date, ver_string)
        self.assertEqual(response.version_info, None)
        response.read_bytestring(data, 0)
        print(response.version_info)


if __name__ == '__main__':
    unittest.main()
