import unittest
from spinnman.messages.scp import SCPRequestHeader
from spinnman.messages.scp.enums import SCPCommand
from spinnman.messages.scp.impl import GetVersion, ReadLink, ReadMemory


class TestSCPMessageAssembly(unittest.TestCase):
    def test_create_new_scp_header(self):
        header = SCPRequestHeader(SCPCommand.CMD_VER)

        self.assertEquals(header.command, SCPCommand.CMD_VER)
        self.assertEquals(header.sequence, 0)

    def test_create_new_ver_scp_pkt(self):
        scp = GetVersion(0, 0, 0)
        self.assertEquals(scp.argument_1, None)
        self.assertEquals(scp.argument_2, None)
        self.assertEquals(scp.argument_3, None)
        self.assertEquals(scp.data, None)

    def test_create_new_link_scp_pkt(self):
        scp = ReadLink(0, 0, 0, 0, 256)
        self.assertEquals(scp.argument_1, 0)
        self.assertEquals(scp.argument_2, 256)
        self.assertEquals(scp.argument_3, 0)
        self.assertEquals(scp.data, None)

    def test_create_new_memory_scp_pkt(self):
        scp = ReadMemory(0, 0, 0, 256)
        self.assertEquals(scp.argument_1, 0)
        self.assertEquals(scp.argument_2, 256)
        self.assertEquals(scp.argument_3, 2)
        self.assertEquals(scp.data, None)


if __name__ == '__main__':
    unittest.main()
