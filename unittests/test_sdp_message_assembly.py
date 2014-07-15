__author__ = 'Petrut'

import unittest
import spinnman.messages.sdp.sdp_message as sdp_msg
import spinnman.exceptions as exc
import spinnman.messages.sdp.sdp_flag as flags
import spinnman.messages.sdp.sdp_header as sdp_header

class TestSDPMessageAssembly(unittest.TestCase):
    def test_create_new_sdp_message(self):
        sdp_h = sdp_header.SDPHeader(flags.SDPFlag.REPLY_NOT_EXPECTED,0,1,0,0,0,1,0,0,0)
        msg = sdp_msg.SDPMessage(sdp_h,bytearray(0))
        self.assertEqual(msg.sdp_header.flags,flags.SDPFlag.REPLY_NOT_EXPECTED)
        self.assertEqual(msg.sdp_header.tag,0)
        self.assertEqual(msg.sdp_header.destination_port,1)
        self.assertEqual(msg.sdp_header.source_port,1)
        self.assertEqual(msg.sdp_header.destination_chip_x,0)
        self.assertEqual(msg.sdp_header.destination_chip_y,0)
        self.assertEqual(msg.sdp_header.source_chip_x,0)
        self.assertEqual(msg.sdp_header.source_chip_y,0)
        self.assertEqual(msg.sdp_header.destination_cpu,0)
        self.assertEqual(msg.sdp_header.source_cpu,0)
        self.assertEqual(msg.data,bytearray(0))
        
        with self.assertRaises(exc.SpinnmanInvalidParameterException):
            msg.sdp_header.flags = flags.SDPFlag.REPLY_EXPECTED
        with self.assertRaises(exc.SpinnmanInvalidParameterException):
            msg.sdp_header.tag = 2
        with self.assertRaises(exc.SpinnmanInvalidParameterException):
            msg.sdp_header.destination_port = 2
        with self.assertRaises(exc.SpinnmanInvalidParameterException):
            msg.sdp_header.source_port = 7
        with self.assertRaises(exc.SpinnmanInvalidParameterException):
            msg.sdp_header.destination_chip_x = 2
        with self.assertRaises(exc.SpinnmanInvalidParameterException):
            msg.sdp_header.destination_chip_y = 3
        with self.assertRaises(exc.SpinnmanInvalidParameterException):
            msg.sdp_header.source_chip_x = 2
        with self.assertRaises(exc.SpinnmanInvalidParameterException):
            msg.sdp_header.source_chip_y = 2
        with self.assertRaises(exc.SpinnmanInvalidParameterException):
            msg.sdp_header.destination_cpu = 2
        with self.assertRaises(exc.SpinnmanInvalidParameterException):
            msg.sdp_header.source_cpu = 31


    def test_create_new_sdp_header(self):
        sdp_h = sdp_header.SDPHeader(flags.SDPFlag.REPLY_NOT_EXPECTED,0,1,0,0,0,1,0,0,0)
        self.assertEqual(sdp_h.flags,flags.SDPFlag.REPLY_NOT_EXPECTED)
        self.assertEqual(sdp_h.tag,0)
        self.assertEqual(sdp_h.destination_port,1)
        self.assertEqual(sdp_h.source_port,1)
        self.assertEqual(sdp_h.destination_chip_x,0)
        self.assertEqual(sdp_h.destination_chip_y,0)
        self.assertEqual(sdp_h.source_chip_x,0)
        self.assertEqual(sdp_h.source_chip_y,0)
        self.assertEqual(sdp_h.destination_cpu,0)
        self.assertEqual(sdp_h.source_cpu,0)

        with self.assertRaises(exc.SpinnmanInvalidParameterException):
            sdp_h.flags = flags.SDPFlag.REPLY_EXPECTED
        with self.assertRaises(exc.SpinnmanInvalidParameterException):
            sdp_h.tag = 2
        with self.assertRaises(exc.SpinnmanInvalidParameterException):
            sdp_h.destination_port = 2
        with self.assertRaises(exc.SpinnmanInvalidParameterException):
            sdp_h.source_port = 7
        with self.assertRaises(exc.SpinnmanInvalidParameterException):
            sdp_h.destination_chip_x = 2
        with self.assertRaises(exc.SpinnmanInvalidParameterException):
            sdp_h.destination_chip_y = 3
        with self.assertRaises(exc.SpinnmanInvalidParameterException):
            sdp_h.source_chip_x = 2
        with self.assertRaises(exc.SpinnmanInvalidParameterException):
            sdp_h.source_chip_y = 2
        with self.assertRaises(exc.SpinnmanInvalidParameterException):
            sdp_h.destination_cpu = 2
        with self.assertRaises(exc.SpinnmanInvalidParameterException):
            sdp_h.source_cpu = 31

    def test_throwing_of_exception_port(self):
        with self.assertRaises(exc.SpinnmanInvalidParameterException):
            sdp_header.SDPHeader(flags.SDPFlag.REPLY_NOT_EXPECTED,-1,1,0,0,0,1,0,0,0)

    def test_throwing_of_exception_coordinates(self):
        with self.assertRaises(exc.SpinnmanInvalidParameterException):
            sdp_header.SDPHeader(flags.SDPFlag.REPLY_NOT_EXPECTED,0,1,-1,0,0,1,0,0,0)


if __name__ == '__main__':
    unittest.main()
