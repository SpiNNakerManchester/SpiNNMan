__author__ = 'Petrut'

import unittest
import spinnman.messages.scp_message as scp_msg
import spinnman.messages.sdp_message as sdp_msg
import spinnman.exceptions as exc
import spinnman.messages.sdp_flag as flags
import spinnman.messages.scp_command as cmds

class TestSDPMessageAssembly(unittest.TestCase):
    def test_create_new_sdp_message(self):
        msg = sdp_msg.SDPMessage(flags.SDPFlag.REPLY_NOT_EXPECTED,1,0,0,0,0,1,0,0,0,bytearray(0))

        self.assertEqual(msg.flags,flags.SDPFlag.REPLY_NOT_EXPECTED)
        self.assertEqual(msg.tag,0)
        self.assertEqual(msg.destination_port,1)
        self.assertEqual(msg.source_port,1)
        self.assertEqual(msg.destination_chip_x,0)
        self.assertEqual(msg.destination_chip_y,0)
        self.assertEqual(msg.source_chip_x,0)
        self.assertEqual(msg.source_chip_y,0)
        self.assertEqual(msg.destination_cpu,0)
        self.assertEqual(msg.source_cpu,0)
        self.assertEqual(msg.data,bytearray(0))

    def test_throwing_of_exception_port(self):
        with self.assertRaises(exc.SpinnmanInvalidParameterException):
             sdp_msg.SDPMessage(flags.SDPFlag.REPLY_NOT_EXPECTED,-1,0,0,0,0,1,0,0,0,bytearray(0))

    def test_throwing_of_exception_coordinates(self):
        with self.assertRaises(exc.SpinnmanInvalidParameterException):
             sdp_msg.SDPMessage(flags.SDPFlag.REPLY_NOT_EXPECTED,1,0,-1,0,0,1,0,0,0,bytearray(0))
if __name__ == '__main__':
    unittest.main()
