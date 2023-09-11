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
from spinnman.config_setup import unittest_setup
from spinnman.messages.eieio import EIEIOPrefix, EIEIOType


class TestEIEIOEnums(unittest.TestCase):

    def setUp(self):
        unittest_setup()

    def test_eieio_prefix(self):
        self.assertEqual(EIEIOPrefix.LOWER_HALF_WORD.value, 0)
        self.assertEqual(EIEIOPrefix(0), EIEIOPrefix.LOWER_HALF_WORD)

        self.assertEqual(EIEIOPrefix.UPPER_HALF_WORD.value, 1)
        self.assertEqual(EIEIOPrefix(1), EIEIOPrefix.UPPER_HALF_WORD)

        self.assertRaises(ValueError, lambda: EIEIOPrefix(2))

    def test_eieio_type(self):
        self.assertEqual(EIEIOType.KEY_16_BIT.value, 0)
        self.assertEqual(EIEIOType.KEY_16_BIT.encoded_value, 0)
        self.assertEqual(EIEIOType.KEY_16_BIT.key_bytes, 2)
        self.assertEqual(EIEIOType.KEY_16_BIT.payload_bytes, 0)
        self.assertEqual(EIEIOType(0), EIEIOType.KEY_16_BIT)

        self.assertEqual(EIEIOType.KEY_PAYLOAD_16_BIT.value, 1)
        self.assertEqual(EIEIOType.KEY_PAYLOAD_16_BIT.encoded_value, 1)
        self.assertEqual(EIEIOType.KEY_PAYLOAD_16_BIT.key_bytes, 2)
        self.assertEqual(EIEIOType.KEY_PAYLOAD_16_BIT.payload_bytes, 2)
        self.assertEqual(EIEIOType(1), EIEIOType.KEY_PAYLOAD_16_BIT)

        self.assertEqual(EIEIOType.KEY_32_BIT.value, 2)
        self.assertEqual(EIEIOType.KEY_32_BIT.encoded_value, 2)
        self.assertEqual(EIEIOType.KEY_32_BIT.key_bytes, 4)
        self.assertEqual(EIEIOType.KEY_32_BIT.payload_bytes, 0)
        self.assertEqual(EIEIOType(2), EIEIOType.KEY_32_BIT)

        self.assertEqual(EIEIOType.KEY_PAYLOAD_32_BIT.value, 3)
        self.assertEqual(EIEIOType.KEY_PAYLOAD_32_BIT.encoded_value, 3)
        self.assertEqual(EIEIOType.KEY_PAYLOAD_32_BIT.key_bytes, 4)
        self.assertEqual(EIEIOType.KEY_PAYLOAD_32_BIT.payload_bytes, 4)
        self.assertEqual(EIEIOType(3), EIEIOType.KEY_PAYLOAD_32_BIT)

        self.assertRaises(ValueError, lambda: EIEIOType(4))


if __name__ == '__main__':
    unittest.main()
