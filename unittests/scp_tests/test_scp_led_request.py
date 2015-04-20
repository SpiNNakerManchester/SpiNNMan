import unittest
from spinnman.messages.scp.impl.scp_led_request import SCPLEDRequest
from spinnman.messages.scp.scp_command import SCPCommand
from spinnman.exceptions import SpinnmanInvalidParameterException

class TestSCPLEDRequest(unittest.TestCase):
    def test_new_led_request(self):
        led_request = SCPLEDRequest(0, 1, 2, {})
        self.assertEqual(
            led_request.scp_request_header.command, SCPCommand.CMD_LED)
        self.assertEqual(led_request.sdp_header.destination_chip_x, 0)
        self.assertEqual(led_request.sdp_header.destination_chip_y, 1)
        self.assertEqual(led_request.sdp_header.destination_cpu, 2)

    def test_new_led_request_invalid_x(self):
        with self.assertRaises(SpinnmanInvalidParameterException):
            led_request = SCPLEDRequest(256, 1, 2, {})

    def test_new_led_request_invalid_y(self):
        with self.assertRaises(SpinnmanInvalidParameterException):
            led_request = SCPLEDRequest(0, 256, 2, {})

    def test_new_led_request_invalid_p(self):
        with self.assertRaises(SpinnmanInvalidParameterException):
            led_request = SCPLEDRequest(0, 1, 32, {})

    def test_new_led_request_invalid_led(self):
        with self.assertRaises(SpinnmanInvalidParameterException):
            led_request = SCPLEDRequest(0, 1, 2, {-1: 0})
        with self.assertRaises(SpinnmanInvalidParameterException):
            led_request = SCPLEDRequest(0, 1, 2, {8: 0})

    def test_new_led_request_invalid_state(self):
        with self.assertRaises(SpinnmanInvalidParameterException):
            led_request = SCPLEDRequest(0, 1, 2, {0: -1})
            led_request = SCPLEDRequest(0, 1, 2, {0: 3})

if __name__ == '__main__':
    unittest.main()
