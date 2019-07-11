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
from spinnman.model import IOBuffer


class TestingIOBuf(unittest.TestCase):
    def test_new_buf(self):
        iobuf = IOBuffer(0, 1, 2, 'Everything failed on chip.')
        self.assertIsNotNone(iobuf)
        self.assertEqual(iobuf.x, 0)
        self.assertEqual(iobuf.y, 1)
        self.assertEqual(iobuf.p, 2)
        self.assertEqual(iobuf.iobuf, 'Everything failed on chip.')


if __name__ == '__main__':
    unittest.main()
