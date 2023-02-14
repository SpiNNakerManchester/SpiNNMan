# Copyright (c) 2014 The University of Manchester
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

import struct
import unittest
from spinnman.config_setup import unittest_setup
from spinnman.exceptions import SpinnmanUnexpectedResponseCodeException
from spinnman.messages.scp.impl import CheckOKResponse
from spinnman.messages.scp.enums import SCPResult
from spinnman.messages.sdp import SDPFlag


class TestOkResponse(unittest.TestCase):

    def setUp(self):
        unittest_setup()

    def test_new_scp_check_ok_response(self):
        CheckOKResponse("Testing operation", "Testing command")

    def _encode_addr_tuple(self, dest_port, dest_cpu, src_port, src_cpu):
        return dest_port << 13 | dest_cpu << 8 | src_port << 5 | src_cpu

    def test_read_ok_response(self):
        scp = CheckOKResponse("Testing operation", "Testing command")
        result = SCPResult.RC_OK.value
        flags = SDPFlag.REPLY_NOT_EXPECTED.value
        tag = 0x01
        flag_tag_short = tag << 8 | flags  # flags << 8 | tag
        dest_port = 7
        dest_cpu = 15
        src_port = 7
        src_cpu = 31
        dest_source_short = self._encode_addr_tuple(
            dest_port, dest_cpu, src_port, src_cpu)

        dest_x = 1
        dest_y = 8

        dest_x_y_short = dest_x << 8 | dest_y

        src_x = 255
        src_y = 0

        src_x_y_short = src_x << 8 | src_y

        seq = 103
        byte_stream = struct.pack('<HHHHHH', flag_tag_short, dest_source_short,
                                  dest_x_y_short, src_x_y_short, result, seq)
        scp.read_bytestring(byte_stream, 0)

    def test_not_ok_response(self):
        with self.assertRaises(SpinnmanUnexpectedResponseCodeException):
            scp = CheckOKResponse("Testing operation", "Testing command")
            result = SCPResult.RC_TIMEOUT.value
            flags = SDPFlag.REPLY_NOT_EXPECTED.value
            tag = 0x01
            flag_tag_short = tag << 8 | flags  # flags << 8 | tag
            dest_port = 7
            dest_cpu = 15
            src_port = 7
            src_cpu = 31
            dest_source_short = self._encode_addr_tuple(
                dest_port, dest_cpu, src_port, src_cpu)

            dest_x = 1
            dest_y = 8

            dest_x_y_short = dest_x << 8 | dest_y

            src_x = 255
            src_y = 0

            src_x_y_short = src_x << 8 | src_y

            seq = 103
            byte_stream = struct.pack('<HHHHHH', flag_tag_short,
                                      dest_source_short, dest_x_y_short,
                                      src_x_y_short, result, seq)
            scp.read_bytestring(byte_stream, 0)


if __name__ == '__main__':
    unittest.main()
