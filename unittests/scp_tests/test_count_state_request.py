import unittest
from spinnman.messages.scp.impl.scp_count_state_request import SCPCountStateRequest
from spinnman.model.cpu_state import CPUState
from spinnman.exceptions import SpinnmanInvalidParameterException


class TestCPUStateRequest(unittest.TestCase):
    def test_new_state_request(self):
        request = SCPCountStateRequest(32,CPUState.READY)

    def test_new_state_request_invalid_app_id(self):
        with self.assertRaises(SpinnmanInvalidParameterException):
            SCPCountStateRequest(256,CPUState.READY)



if __name__ == '__main__':
    unittest.main()
