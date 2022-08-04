# Copyright (c) 2021-2022 The University of Manchester
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
from spinn_utilities.exceptions import (DataNotYetAvialable)
from spinnman.config_setup import unittest_setup
from spinnman.data import SpiNNManDataView
from spinnman.data.spinnman_data_writer import SpiNNManDataWriter
from spinnman.transceiver import Transceiver


class MockTranceiver(Transceiver):

    def __init__(self):
        """
        Hide normal init
        """


class TestData(unittest.TestCase):

    def setUp(cls):
        unittest_setup()

    def test_setup(self):
        # What happens before setup depends on the previous test
        # Use manual_check to verify this without dependency
        SpiNNManDataWriter.setup()
        with self.assertRaises(DataNotYetAvialable):
            SpiNNManDataView.get_transceiver()

    def test_mock(self):
        SpiNNManDataWriter.mock()
        # check there is a
        #   value not what it is
        SpiNNManDataView.get_machine()

    def test_transceiver(self):
        writer = SpiNNManDataWriter.setup()
        with self.assertRaises(DataNotYetAvialable):
            SpiNNManDataView.get_transceiver()
        self.assertFalse(SpiNNManDataView.has_transceiver())
        writer.set_transceiver(MockTranceiver())
        SpiNNManDataView.get_transceiver()
        self.assertTrue(SpiNNManDataView.has_transceiver())
        with self.assertRaises(TypeError):
            writer.set_transceiver("bacon")
