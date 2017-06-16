import unittest
from struct import pack

from spinnman.exceptions import SpinnmanUnexpectedResponseCodeException
from spinnman.messages.scp.impl.scp_count_state_response \
    import SCPCountStateResponse
from spinnman.messages.scp.enums import SCPResult
from spinnman.messages.sdp import SDPFlag


class TestCPUStateResponse(unittest.TestCase):
    def test_new_count_state_response(self):
        response = SCPCountStateResponse()
        # SCP Stuff
        rc = SCPResult.RC_OK.value
        seq = 105

        argument_count = 5
        # SDP stuff
        flags = SDPFlag.REPLY_NOT_EXPECTED.value
        tag = 5
        dest_port_cpu = 0x4f
        srce_port_cpu = 0x6a
        dest_x = 0x11
        dest_y = 0xab
        srce_x = 0x7
        srce_y = 0x0
        data = pack('<8BHHI', flags, tag, dest_port_cpu, srce_port_cpu, dest_y,
                    dest_x, srce_y, srce_x, rc, seq, argument_count)
        response.read_bytestring(data, 0)
        self.assertEqual(response.count, 5)

    def test_new_count_state_response_response_not_ok(self):
        with self.assertRaises(SpinnmanUnexpectedResponseCodeException):
            response = SCPCountStateResponse()
            # SCP Stuff
            rc = SCPResult.RC_TIMEOUT.value
            seq = 105
            p2p_addr = 1024
            phys_cpu = 31
            virt_cpu = 14
            version = 234
            buffer = 250
            build_date = 103117
            ver_string = "sark/spinnaker"

            # SDP stuff
            flags = SDPFlag.REPLY_NOT_EXPECTED.value
            tag = 5
            dest_port_cpu = 0x4f
            srce_port_cpu = 0x6a
            dest_x = 0x11
            dest_y = 0xab
            srce_x = 0x7
            srce_y = 0x0
            data = pack('<8BHHHBBHHI15s', flags, tag, dest_port_cpu,
                        srce_port_cpu, dest_y, dest_x, srce_y, srce_x, rc, seq,
                        p2p_addr, phys_cpu, virt_cpu, version, buffer,
                        build_date, ver_string)
            response.read_bytestring(data, 0)


if __name__ == '__main__':
    unittest.main()
