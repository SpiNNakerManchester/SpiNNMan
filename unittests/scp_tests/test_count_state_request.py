import unittest

from spinnman.messages.scp.impl.scp_count_state_request \
    import SCPCountStateRequest
from spinnman.model.enums.cpu_state import CPUState


class TestCPUStateRequest(unittest.TestCase):
    def test_new_state_request(self):
        request = SCPCountStateRequest(32, CPUState.READY)
        self.assertIsNotNone(request, "must make a SCPCountStateRequest")


if __name__ == '__main__':
    unittest.main()
