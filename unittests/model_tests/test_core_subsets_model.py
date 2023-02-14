# Copyright (c) 2014 The University of Manchester
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
