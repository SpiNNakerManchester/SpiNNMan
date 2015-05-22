import unittest
from spinnman.messages.scp.impl.scp_version_response import SCPVersionResponse
from spinnman.data.little_endian_byte_array_byte_reader \
    import LittleEndianByteArrayByteReader
from struct import pack
from spinnman.messages.scp.scp_result import SCPResult
from spinnman.messages.sdp.sdp_flag import SDPFlag


class TestSCPVersionResponse(unittest.TestCase):
    def test_new_scp_version_response(self):
        SCPVersionResponse()

    def test_read_scp_response(self):
        response = SCPVersionResponse()
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
        data = pack(
            '<8BHHHBBHHI15s', flags, tag, dest_port_cpu, srce_port_cpu, dest_y,
            dest_x, srce_y, srce_x, rc, seq, p2p_addr, phys_cpu, virt_cpu,
            version, buffer, build_date, ver_string)
        data = bytearray(data)
        reader = LittleEndianByteArrayByteReader(data)
        self.assertEqual(response.version_info, None)
        response.read_scp_response(reader)
        print response.version_info

if __name__ == '__main__':
    unittest.main()
