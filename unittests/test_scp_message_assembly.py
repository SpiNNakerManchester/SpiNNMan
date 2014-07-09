__author__ = 'Petrut'

import unittest
import spinnman.messages.scp_message as scp_msg
import spinnman.messages.sdp_message as sdp_msg
import spinnman.exceptions as exc

class TestSCPMessageAssembly(unittest.TestCase):
    def test_create_new_scp_message(self):
        msg = scp_msg.SCPMessage(sdp_msg.Flag.REPLY_NOT_EXPECTED, 0, 1, 0, 0, 0, 1, 0, 0, 0,
                                 scp_msg.Command.CMD_APLX, 0, 1, 2, 3, bytearray(0))

        self.assertEqual(msg.flags,sdp_msg.Flag.REPLY_NOT_EXPECTED)
        self.assertEqual(msg.argument_1,1)
        self.assertEqual(msg.argument_2,2)
        self.assertEqual(msg.argument_3,3)
        self.assertEqual(msg.command,scp_msg.Command.CMD_APLX)
        self.assertEqual(msg.tag,0)
        self.assertEqual(msg.destination_port,1)
        self.assertEqual(msg.source_port,1)
        self.assertEqual(msg.destination_chip_x,0)
        self.assertEqual(msg.destination_chip_y,0)
        self.assertEqual(msg.source_chip_x,0)
        self.assertEqual(msg.source_chip_y,0)
        self.assertEqual(msg.destination_cpu,0)
        self.assertEqual(msg.destination_cpu,0)
        self.assertEqual(msg.sequence,0)
        #self.assertEqual(msg.data,bytearray(0))
    """
    def test_throwing_of_exception_flag(self):
        with self.assertRaises(exc.SpinnmanInvalidParameterException):
            msg = scp_msg.SCPMessage(-1,0,1,0,0,0,1,0,0,0,scp_msg.Command.CMD_APLX,0,1,2,3,bytearray(0))

    def test_throwing_of_exception_command(self):
        with self.assertRaises(exc.SpinnmanInvalidParameterException):
            msg = scp_msg.SCPMessage(sdp_msg.Flag.REPLY_NOT_EXPECTED,0,1,0,0,0,1,0,0,0,-1,0,1,2,3,bytearray(0))

    def test_throwing_of_exception_data(self):
        with self.assertRaises(exc.SpinnmanInvalidParameterException):
            msg = scp_msg.SCPMessage(sdp_msg.Flag.REPLY_NOT_EXPECTED,0,1,0,0,0,1,0,0,0,scp_msg.Command.CMD_APLX,0,1,2,3,0)
    """
    def test_throwing_of_exception_port(self):
        with self.assertRaises(exc.SpinnmanInvalidParameterException):
             msg = scp_msg.SCPMessage(sdp_msg.Flag.REPLY_NOT_EXPECTED, 0, -1, 0, 0, 0, 1, 0, 0, 0,
                                 scp_msg.Command.CMD_APLX, 0, 1, 2, 3, bytearray(0))

    def test_throwing_of_exception_coordinates(self):
        with self.assertRaises(exc.SpinnmanInvalidParameterException):
             msg = scp_msg.SCPMessage(sdp_msg.Flag.REPLY_NOT_EXPECTED, 0, 1, -1, 0, 0, 1, 0, 0, 0,
                                 scp_msg.Command.CMD_APLX, 0, 1, 2, 3, bytearray(0))

if __name__ == '__main__':
    unittest.main()
