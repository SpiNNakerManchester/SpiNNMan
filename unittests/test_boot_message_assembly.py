# Copyright (c) 2014 The University of Manchester
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
import spinnman.messages.spinnaker_boot.spinnaker_boot_message as boot_msg
from spinnman.config_setup import unittest_setup
from spinnman.messages.spinnaker_boot import SpinnakerBootOpCode


class TestSpiNNakerBootMessage(unittest.TestCase):

    def setUp(self) -> None:
        unittest_setup()

    def test_create_new_boot_message(self) -> None:
        msg = boot_msg.SpinnakerBootMessage(SpinnakerBootOpCode.HELLO, 0, 0, 0)
        self.assertEqual(msg.data, None)
        self.assertEqual(msg.opcode, SpinnakerBootOpCode.HELLO)
        self.assertEqual(msg.operand_1, 0)
        self.assertEqual(msg.operand_2, 0)
        self.assertEqual(msg.operand_3, 0)


if __name__ == '__main__':
    unittest.main()
