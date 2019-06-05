import unittest
import spinnman.messages.spinnaker_boot.spinnaker_boot_message as boot_msg
from spinnman.messages.spinnaker_boot import SpinnakerBootOpCode


class TestSpiNNakerBootMessage(unittest.TestCase):
    def test_create_new_boot_message(self):
        msg = boot_msg.SpinnakerBootMessage(SpinnakerBootOpCode.HELLO, 0, 0, 0)
        self.assertEquals(msg.data, None)
        self.assertEquals(msg.opcode, SpinnakerBootOpCode.HELLO)
        self.assertEquals(msg.operand_1, 0)
        self.assertEquals(msg.operand_2, 0)
        self.assertEquals(msg.operand_3, 0)


if __name__ == '__main__':
    unittest.main()
