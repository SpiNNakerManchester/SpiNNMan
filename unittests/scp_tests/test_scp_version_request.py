import unittest
from spinnman.messages.scp.impl import GetVersion
from spinnman.messages.scp.enums import SCPCommand


class TestSCPVersionRequest(unittest.TestCase):
    def test_new_version_request(self):
        ver_request = GetVersion(0, 1, 2)
        self.assertEqual(ver_request.scp_request_header.command,
                         SCPCommand.CMD_VER)
        self.assertEqual(ver_request.sdp_header.destination_chip_x, 0)
        self.assertEqual(ver_request.sdp_header.destination_chip_y, 1)
        self.assertEqual(ver_request.sdp_header.destination_cpu, 2)


if __name__ == '__main__':
    unittest.main()
