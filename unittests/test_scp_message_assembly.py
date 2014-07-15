__author__ = 'Petrut'

import unittest
import spinnman.messages.scp.scp_request_header as scp_req
import spinnman.exceptions as exc
import spinnman.messages.scp.scp_command as cmds

class TestSCPMessageAssembly(unittest.TestCase):
    def test_create_new_scp_message(self):
        msg = scp_req.SCPRequestHeader(cmds.SCPCommand.CMD_VER)

        self.assertEqual(msg.command,cmds.SCPCommand.CMD_VER)
        self.assertEqual(msg.sequence,None)
        #self.assertEqual(msg.data,bytearray(0))

    def test_throwing_of_exception_sequence(self):
        with self.assertRaises(exc.SpinnmanInvalidParameterException):
             scp_req.SCPRequestHeader(cmds.SCPCommand.CMD_APLX, -1)


if __name__ == '__main__':
    unittest.main()
