import unittest

import spinnman.messages.scp.scp_request_header as scp_req
import spinnman.messages.scp.enums.scp_command as cmds
import spinnman.messages.scp.impl.scp_version_request as ver_req
from spinnman.messages.scp.impl.scp_read_link_request import SCPReadLinkRequest
from spinnman.messages.scp.impl.scp_read_memory_request \
    import SCPReadMemoryRequest


class TestSCPMessageAssembly(unittest.TestCase):
    def test_create_new_scp_header(self):
        header = scp_req.SCPRequestHeader(cmds.SCPCommand.CMD_VER)

        self.assertEqual(header.command, cmds.SCPCommand.CMD_VER)
        self.assertEqual(header.sequence, 0)

    def test_create_new_ver_scp_pkt(self):
        scp = ver_req.SCPVersionRequest(0, 0, 0)
        self.assertEqual(scp.argument_1, None)
        self.assertEqual(scp.argument_2, None)
        self.assertEqual(scp.argument_3, None)
        self.assertEqual(scp.data, None)

    def test_create_new_link_scp_pkt(self):
        scp = SCPReadLinkRequest(0, 0, 0, 0, 256)
        self.assertEqual(scp.argument_1, 0)
        self.assertEqual(scp.argument_2, 256)
        self.assertEqual(scp.argument_3, 0)
        self.assertEqual(scp.data, None)

    def test_create_new_memory_scp_pkt(self):
        scp = SCPReadMemoryRequest(0, 0, 0, 256)
        self.assertEqual(scp.argument_1, 0)
        self.assertEqual(scp.argument_2, 256)
        self.assertEqual(scp.argument_3, 2)
        self.assertEqual(scp.data, None)


if __name__ == '__main__':
    unittest.main()
