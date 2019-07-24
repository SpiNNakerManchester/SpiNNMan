# Copyright (c) 2017-2019 The University of Manchester
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import unittest
import spinnman.messages.spinnaker_boot.spinnaker_boot_message as boot_msg
from spinnman.messages.spinnaker_boot import SpinnakerBootOpCode


class TestSpiNNakerBootMessage(unittest.TestCase):
    def test_create_new_boot_message(self):
        msg = boot_msg.SpinnakerBootMessage(SpinnakerBootOpCode.HELLO, 0, 0, 0)
        self.assertEqual(msg.data, None)
        self.assertEqual(msg.opcode, SpinnakerBootOpCode.HELLO)
        self.assertEqual(msg.operand_1, 0)
        self.assertEqual(msg.operand_2, 0)
        self.assertEqual(msg.operand_3, 0)


if __name__ == '__main__':
    unittest.main()
