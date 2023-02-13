# Copyright (c) 2021-2023 The University of Manchester
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
