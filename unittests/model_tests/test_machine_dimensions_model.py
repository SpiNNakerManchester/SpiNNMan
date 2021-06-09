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
from spinnman.model import MachineDimensions
from spinnman.config_setup import unittest_setup


class TestMachineDimensionsModel(unittest.TestCase):

    def setUp(self):
        unittest_setup()

    def test_new_iptag(self):
        x_max = 253
        y_max = 220
        machine_dim = MachineDimensions(x_max, y_max)
        self.assertEqual(x_max, machine_dim.width)
        self.assertEqual(y_max, machine_dim.height)


if __name__ == '__main__':
    unittest.main()
