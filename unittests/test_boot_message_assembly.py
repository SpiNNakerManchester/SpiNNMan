__author__ = 'Petrut'

import unittest
import spinnman.exceptions as exc
import spinnman.messages.spinnaker_boot_message as boot_msg

class TestSpiNNakerBootMessage(unittest.TestCase):
    def test_create_new_boot_message(self):
        msg = boot_msg.SpinnakerBootMessage(boot_msg.OpCode.HELLO,0,0,0)

    def test_raise_exception(self):
        with self.assertRaises(exc.SpinnmanInvalidParameterException):
            msg = boot_msg.SpinnakerBootMessage(boot_msg.OpCode.HELLO,None,None,None)

    def test_raise_exception_op_code(self):
        with self.assertRaises(exc.SpinnmanInvalidParameterException):
            msg = boot_msg.SpinnakerBootMessage(5,0,0,0)


if __name__ == '__main__':
    unittest.main()
