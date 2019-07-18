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
from struct import pack
from spinnman.exceptions import SpinnmanUnexpectedResponseCodeException
from spinnman.messages.scp.impl.count_state_response import (
    CountStateResponse)
from spinnman.messages.scp.enums import SCPResult
from spinnman.messages.sdp import SDPFlag


class TestCPUStateResponse(unittest.TestCase):
    def test_new_count_state_response(self):
        response = CountStateResponse()
        # SCP Stuff
        rc = SCPResult.RC_OK.value
        seq = 105

        argument_count = 5
        # SDP stuff
        flags = SDPFlag.REPLY_NOT_EXPECTED.value
        tag = 5
        dest_port_cpu = 0x4f
        src_port_cpu = 0x6a
        dest_x = 0x11
        dest_y = 0xab
        src_x = 0x7
        src_y = 0x0
        data = pack('<8BHHI', flags, tag, dest_port_cpu, src_port_cpu, dest_y,
                    dest_x, src_y, src_x, rc, seq, argument_count)
        response.read_bytestring(data, 0)
        self.assertEqual(response.count, 5)

    def test_new_count_state_response_response_not_ok(self):
        with self.assertRaises(SpinnmanUnexpectedResponseCodeException):
            response = CountStateResponse()
            # SCP Stuff
            rc = SCPResult.RC_TIMEOUT.value
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
            data = pack('<8BHHHBBHHI15s', flags, tag, dest_port_cpu,
                        src_port_cpu, dest_y, dest_x, src_y, src_x, rc, seq,
                        p2p_addr, phys_cpu, virt_cpu, version, buffer,
                        build_date, ver_string)
            response.read_bytestring(data, 0)


if __name__ == '__main__':
    unittest.main()
