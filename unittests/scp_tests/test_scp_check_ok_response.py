import struct
import unittest

from spinnman.exceptions import SpinnmanUnexpectedResponseCodeException
from spinnman.messages.scp.impl.scp_check_ok_response \
    import SCPCheckOKResponse, SCPResult
from spinnman.messages.sdp.sdp_flag import SDPFlag


class TestOkResponse(unittest.TestCase):
    def test_new_scp_check_ok_response(self):
        SCPCheckOKResponse("Testing operation", "Testing command")

    def test_read_ok_response(self):
        scp = SCPCheckOKResponse("Testing operation", "Testing command")
        result = SCPResult.RC_OK.value
        flags = SDPFlag.REPLY_NOT_EXPECTED.value
        tag = 0x01
        flag_tag_short = tag << 8 | flags  # flags << 8 | tag
        dest_port = 7
        dest_cpu = 15
        srce_port = 7
        srce_cpu = 31
        dest_source_short = dest_port << 13 | dest_cpu << 8 | srce_port << 5 \
            | srce_cpu

        dest_x = 1
        dest_y = 8

        dest_x_y_short = dest_x << 8 | dest_y

        srce_x = 255
        srce_y = 0

        srce_x_y_short = srce_x << 8 | srce_y

        seq = 103
        byte_stream = struct.pack('<HHHHHH', flag_tag_short, dest_source_short,
                                  dest_x_y_short, srce_x_y_short, result, seq)
        scp.read_bytestring(byte_stream, 0)

    def test_not_ok_response(self):
        with self.assertRaises(SpinnmanUnexpectedResponseCodeException):
            scp = SCPCheckOKResponse("Testing operation", "Testing command")
            result = SCPResult.RC_TIMEOUT.value
            flags = SDPFlag.REPLY_NOT_EXPECTED.value
            tag = 0x01
            flag_tag_short = tag << 8 | flags  # flags << 8 | tag
            dest_port = 7
            dest_cpu = 15
            srce_port = 7
            srce_cpu = 31
            dest_source_short = dest_port << 13 | dest_cpu << 8 | \
                srce_port << 5 | srce_cpu

            dest_x = 1
            dest_y = 8

            dest_x_y_short = dest_x << 8 | dest_y

            srce_x = 255
            srce_y = 0

            srce_x_y_short = srce_x << 8 | srce_y

            seq = 103
            byte_stream = struct.pack('<HHHHHH', flag_tag_short,
                                      dest_source_short, dest_x_y_short,
                                      srce_x_y_short, result, seq)
            scp.read_bytestring(byte_stream, 0)


if __name__ == '__main__':
    unittest.main()
