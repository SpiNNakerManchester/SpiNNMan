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
from spinnman.messages.sdp.sdp_flag import SDPFlag


class TestSDPEnums(unittest.TestCase):
    def test_sdp_flag(self):
        self.assertEqual(SDPFlag.REPLY_NOT_EXPECTED.value, 0x7)
        self.assertEqual(SDPFlag.REPLY_EXPECTED.value, 0x87)


if __name__ == '__main__':
    unittest.main()
