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
