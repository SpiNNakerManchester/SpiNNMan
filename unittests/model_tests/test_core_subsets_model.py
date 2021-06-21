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
from spinn_machine import CoreSubset, CoreSubsets
from spinnman.config_setup import unittest_setup


class TestCoreSubsets(unittest.TestCase):

    def setUp(self):
        unittest_setup()

    def test_create_new_default_core_subsets(self):
        css = CoreSubsets()
        self.assertIsNotNone(css, "must make instance of CoreSubsets")

    def test_create_new_core_subsets(self):
        proc_list = [0, 1, 2, 3, 5, 8, 13]
        cs = CoreSubset(0, 0, proc_list)
        css = CoreSubsets([cs])
        self.assertIn(cs, css.core_subsets)
        for core_subset in css.core_subsets:
            self.assertIn(core_subset, [cs])

    def test_add_processor_duplicate_processor(self):
        proc_list = [0, 1, 2, 3, 5, 8, 13]
        cs = CoreSubset(0, 0, proc_list)
        css = CoreSubsets([cs])
        css.add_processor(0, 0, 0)

    def test_add_processor_duplicate_processor_different_chip(self):
        proc_list = [0, 1, 2, 3, 5, 8, 13]
        cs = CoreSubset(0, 0, proc_list)
        css = CoreSubsets([cs])
        css.add_processor(0, 1, 0)

    def test_add_core_subset_duplicate_core_subset(self):
        proc_list = [0, 1, 2, 3, 5, 8, 13]
        cs = CoreSubset(0, 0, proc_list)
        css = CoreSubsets([cs])
        css.add_core_subset(cs)

    def test_add_core_subset(self):
        proc_list = [0, 1, 2, 3, 5, 8, 13]
        cs = CoreSubset(0, 0, proc_list)
        css = CoreSubsets()
        css.add_core_subset(cs)
        self.assertIn(cs, css.core_subsets)
        for core_subset in css.core_subsets:
            self.assertIn(core_subset, [cs])

    def test_add_processor(self):
        proc_list = [0, 1, 2, 3, 5, 8, 13]
        cs = CoreSubset(0, 0, proc_list)
        css = CoreSubsets()
        css.add_core_subset(cs)
        self.assertIn(cs, css.core_subsets)
        for core_subset in css.core_subsets:
            self.assertIn(core_subset, [cs])


if __name__ == '__main__':
    unittest.main()
