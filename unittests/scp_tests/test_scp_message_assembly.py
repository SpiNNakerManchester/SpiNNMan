import unittest
import spinnman.messages.scp.scp_request_header as scp_req
import spinnman.exceptions as exc
import spinnman.messages.scp.scp_command as cmds
import spinnman.messages.scp.impl.scp_version_request as ver_req
from spinnman.messages.scp.impl.scp_read_link_request import SCPReadLinkRequest
from spinnman.messages.scp.impl.scp_read_memory_request import SCPReadMemoryRequest

class TestSCPMessageAssembly(unittest.TestCase):
    def test_create_new_scp_header(self):
        header = scp_req.SCPRequestHeader(cmds.SCPCommand.CMD_VER)

        self.assertEqual(header.command,cmds.SCPCommand.CMD_VER)
        self.assertEqual(header.sequence,None)

    def test_throwing_of_exception_sequence(self):
        with self.assertRaises(exc.SpinnmanInvalidParameterException):
             scp_req.SCPRequestHeader(cmds.SCPCommand.CMD_APLX, -1)

    def test_create_new_ver_scp_pkt(self):
        scp = ver_req.SCPVersionRequest(0,0,0)
        self.assertEqual(scp.argument_1,None)
        self.assertEqual(scp.argument_2,None)
        self.assertEqual(scp.argument_3,None)
        self.assertEqual(scp.data,None)

    def test_create_new_ver_scp_pkt_with_invalid_x(self):
        with self.assertRaises(exc.SpinnmanInvalidParameterException):
            ver_req.SCPVersionRequest(256,0,0)

    def test_create_new_ver_scp_pkt_with_invalid_y(self):
        with self.assertRaises(exc.SpinnmanInvalidParameterException):
            ver_req.SCPVersionRequest(0,256,0)

    def test_create_new_ver_scp_pkt_with_invalid_processor_negative(self):
        with self.assertRaises(exc.SpinnmanInvalidParameterException):
            ver_req.SCPVersionRequest(0,0,-1)

    def test_create_new_ver_scp_pkt_with_invalid_processor_greater_than_31(self):
        with self.assertRaises(exc.SpinnmanInvalidParameterException):
            ver_req.SCPVersionRequest(0,0,32)
            
    def test_create_new_link_scp_pkt(self):
        scp = SCPReadLinkRequest(0,0,0,0,256)
        self.assertEqual(scp.argument_1,0)
        self.assertEqual(scp.argument_2,256)
        self.assertEqual(scp.argument_3,0)
        self.assertEqual(scp.data,None)

    def test_create_new_link_scp_pkt_with_invalid_x(self):
        with self.assertRaises(exc.SpinnmanInvalidParameterException):
            SCPReadLinkRequest(256,0,0,0,256)

    def test_create_new_link_scp_pkt_with_invalid_y(self):
        with self.assertRaises(exc.SpinnmanInvalidParameterException):
            SCPReadLinkRequest(0,256,0,0,256)

    def test_create_new_link_scp_pkt_with_invalid_data_size(self):
        with self.assertRaises(exc.SpinnmanInvalidParameterException):
            SCPReadLinkRequest(0,0,0,0,257)

    def test_create_new_link_scp_pkt_with_invalid_data_size_0(self):
        with self.assertRaises(exc.SpinnmanInvalidParameterException):
            SCPReadLinkRequest(0,0,0,0,0)

    def test_create_new_memory_scp_pkt(self):
        scp = SCPReadMemoryRequest(0,0,0,256)
        self.assertEqual(scp.argument_1,0)
        self.assertEqual(scp.argument_2,256)
        self.assertEqual(scp.argument_3,0)
        self.assertEqual(scp.data,None)

    def test_create_new_memory_scp_pkt_with_invalid_x(self):
        with self.assertRaises(exc.SpinnmanInvalidParameterException):
            SCPReadMemoryRequest(256,0,0,256)

    def test_create_new_memory_scp_pkt_with_invalid_y(self):
        with self.assertRaises(exc.SpinnmanInvalidParameterException):
            SCPReadMemoryRequest(0,256,0,256)

    def test_create_new_memory_scp_pkt_with_invalid_data_size(self):
        with self.assertRaises(exc.SpinnmanInvalidParameterException):
            SCPReadMemoryRequest(0,0,0,257)

    def test_create_new_memory_scp_pkt_with_invalid_data_size_0(self):
        with self.assertRaises(exc.SpinnmanInvalidParameterException):
            SCPReadMemoryRequest(0,0,0,0)

if __name__ == '__main__':
    unittest.main()
