__author__ = 'Petrut'

import unittest
import spinnman.messages.scp_message as scp_msg
import spinnman.messages.sdp_message as sdp_msg
import spinnman.exceptions as exc

class TestSDPMessageAssembly(unittest.TestCase):
    def test_create_new_sdp_message(self):
        msg = sdp_msg.SDPMessage(sdp_msg.Flag.REPLY_NOT_EXPECTED,0,1,0,0,0,1,0,0,0,bytearray(0))

        self.assertEqual(scp_msg.flag,sdp_msg.Flag.REPLY_NOT_EXPECTED)
        self.assertEqual(scp_msg.tag,0)
        self.assertEqual(scp_msg.destination_port,1)
        self.assertEqual(scp_msg.source_port,1)
        self.assertEqual(scp_msg.destination_chip_x,0)
        self.assertEqual(scp_msg.destination_chip_y,0)
        self.assertEqual(scp_msg.source_chip_x,0)
        self.assertEqual(scp_msg.source_chip_y,0)
        self.assertEqual(scp_msg.destination_cpu,0)
        self.assertEqual(scp_msg.destination_cpu,0)
        self.assertEqual(scp_msg.data,bytearray(0))

    def test_throwing_of_exception_flag(self):
        with self.assertRaises(exc.SpinnmanInvalidParameterException):
            msg = scp_msg.SCPMessage(5,0,1,0,0,0,1,0,0,0,scp_msg.Command.CMD_APLX,0,1,2,3,bytearray(0))

    def test_throwing_of_exception_command(self):
        with self.assertRaises(exc.SpinnmanInvalidParameterException):
            msg = scp_msg.SCPMessage(sdp_msg.Flag.REPLY_NOT_EXPECTED,0,1,0,0,0,1,0,0,0,10,0,1,2,3,bytearray(0))

    def test_throwing_of_exception_data(self):
        with self.assertRaises(exc.SpinnmanInvalidParameterException):
            msg = scp_msg.SCPMessage(sdp_msg.Flag.REPLY_NOT_EXPECTED,0,1,0,0,0,1,0,0,0,scp_msg.Command.CMD_APLX,0,1,2,3,0)

if __name__ == '__main__':
    unittest.main()
