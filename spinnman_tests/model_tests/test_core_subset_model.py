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
