import unittest

from spinnman.messages.scp import SCPRequestHeader
from spinnman.messages.scp.enums import SCPCommand
from spinnman.messages.scp.impl \
    import SCPVersionRequest, SCPReadLinkRequest, SCPReadMemoryRequest


class TestSCPMessageAssembly(unittest.TestCase):
    def test_create_new_scp_header(self):
        header = SCPRequestHeader(SCPCommand.CMD_VER)

        self.assertEqual(header.command, SCPCommand.CMD_VER)
        self.assertEqual(header.sequence, 0)

    def test_create_new_ver_scp_pkt(self):
        scp = SCPVersionRequest(0, 0, 0)
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
