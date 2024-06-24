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
