import unittest

from spinnman.messages.scp import SCPRequestHeader
from spinnman.messages.scp.enums import SCPCommand
from spinnman.messages.scp.impl \
    import GetVersion, ReadLink, ReadMemory


class TestSCPMessageAssembly(unittest.TestCase):
    def test_create_new_scp_header(self):
        header = SCPRequestHeader(SCPCommand.CMD_VER)

        self.assertEqual(header.command, SCPCommand.CMD_VER)
        self.assertEqual(header.sequence, 0)

    def test_create_new_ver_scp_pkt(self):
        scp = GetVersion(0, 0, 0)
        self.assertEqual(scp.argument_1, None)
        self.assertEqual(scp.argument_2, None)
        self.assertEqual(scp.argument_3, None)
        self.assertEqual(scp.data, None)

    def test_create_new_link_scp_pkt(self):
        scp = ReadLink(0, 0, 0, 0, 256)
        self.assertEqual(scp.argument_1, 0)
        self.assertEqual(scp.argument_2, 256)
        self.assertEqual(scp.argument_3, 0)
        self.assertEqual(scp.data, None)

    def test_create_new_memory_scp_pkt(self):
        scp = ReadMemory(0, 0, 0, 256)
        self.assertEqual(scp.argument_1, 0)
        self.assertEqual(scp.argument_2, 256)
        self.assertEqual(scp.argument_3, 2)
        self.assertEqual(scp.data, None)


if __name__ == '__main__':
    unittest.main()
