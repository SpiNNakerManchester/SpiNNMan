import unittest
from spinnman.messages.scp.impl import CountState
from spinnman.model.enums import CPUState


class TestCPUStateRequest(unittest.TestCase):
    def test_new_state_request(self):
        request = CountState(32, CPUState.READY)
        self.assertIsNotNone(request, "must make a CountState")


if __name__ == '__main__':
    unittest.main()
