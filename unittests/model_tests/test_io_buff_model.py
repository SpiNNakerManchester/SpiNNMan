# Copyright (c) 2014-2023 The University of Manchester
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
from spinnman.model import IOBuffer
from spinnman.config_setup import unittest_setup


class TestingIOBuf(unittest.TestCase):

    def setUp(self):
        unittest_setup()

    def test_new_buf(self):
        iobuf = IOBuffer(0, 1, 2, 'Everything failed on chip.')
        self.assertIsNotNone(iobuf)
        self.assertEqual(iobuf.x, 0)
        self.assertEqual(iobuf.y, 1)
        self.assertEqual(iobuf.p, 2)
        self.assertEqual(iobuf.iobuf, 'Everything failed on chip.')


if __name__ == '__main__':
    unittest.main()
