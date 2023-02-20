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
from spinnman.config_setup import unittest_setup
import spinnman.messages.multicast_message as multicast_msg


class TestMulticastMessage(unittest.TestCase):

    def setUp(self):
        unittest_setup()

    def test_create_new_multicast_message_without_payload(self):
        msg = multicast_msg.MulticastMessage(1)
        self.assertEqual(msg.key, 1)
        self.assertEqual(msg.payload, None)

    def test_create_new_multicast_message_with_payload(self):
        msg = multicast_msg.MulticastMessage(1, 100)
        self.assertEqual(msg.key, 1)
        self.assertEqual(msg.payload, 100)


if __name__ == '__main__':
    unittest.main()
