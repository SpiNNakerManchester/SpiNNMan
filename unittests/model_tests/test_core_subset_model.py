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
from spinn_machine import CoreSubset
from spinnman.config_setup import unittest_setup


class TestCoreSubset(unittest.TestCase):

    def setUp(self):
        unittest_setup()

    def test_create_new_core_subset(self):
        proc_list = [0, 1, 2, 3, 5, 8, 13]
        cs = CoreSubset(0, 0, proc_list)
        self.assertEqual(cs.x, 0)
        self.assertEqual(cs.y, 0)
        for proc in cs.processor_ids:
            self.assertIn(proc, proc_list)
        self.assertEqual(len([x for x in cs.processor_ids]), len(proc_list))

    def test_create_new_core_subset_duplicate_processors(self):
        cs = CoreSubset(0, 0, [0, 1, 1, 2, 3, 5, 8, 13])
        self.assertIsNotNone(cs, "must make instance of CoreSubset")

    def test_create_empty_core_subset_add_processor(self):
        proc_list = [0, 1, 2, 3, 5, 8, 13]
        cs = CoreSubset(0, 0, [])
        self.assertEqual(cs.x, 0)
        self.assertEqual(cs.y, 0)
        for proc in proc_list:
            cs.add_processor(proc)
        for proc in cs.processor_ids:
            self.assertIn(proc, proc_list)
        self.assertEqual(len([x for x in cs.processor_ids]), len(proc_list))


if __name__ == '__main__':
    unittest.main()
