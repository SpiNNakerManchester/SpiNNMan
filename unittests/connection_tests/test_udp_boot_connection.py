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
from spinnman.connections.udp_packet_connections import BootConnection
from spinnman.config_setup import unittest_setup


class MyTestCase(unittest.TestCase):

    def setUp(self):
        unittest_setup()

    def test_something(self):
        udp_connect = BootConnection()
        self.assertIsNotNone(udp_connect)


if __name__ == '__main__':
    unittest.main()
