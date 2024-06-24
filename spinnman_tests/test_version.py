# Copyright (c) 2017 The University of Manchester
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
import spinn_utilities
import spinn_machine
from spinnman.transceiver.base_transceiver import (
    BaseTransceiver, _SCAMP_VERSION)
import spinnman
from spinnman.config_setup import unittest_setup


class Test(unittest.TestCase):
    """ Tests for the SCAMP version comparison
    """

    def setUp(self):
        unittest_setup()

    def test_version_same(self):
        self.assertTrue(BaseTransceiver._is_scamp_version_compabible((
            _SCAMP_VERSION[0], _SCAMP_VERSION[1], _SCAMP_VERSION[2])))

    def test_major_version_too_big(self):
        self.assertFalse(BaseTransceiver._is_scamp_version_compabible((
            _SCAMP_VERSION[0] + 1, 0, 0)))

    def test_major_version_too_small(self):
        self.assertFalse(BaseTransceiver._is_scamp_version_compabible((
            _SCAMP_VERSION[0] - 1, 0, 0)))

    def test_minor_version_bigger(self):
        self.assertTrue(BaseTransceiver._is_scamp_version_compabible((
            _SCAMP_VERSION[0], _SCAMP_VERSION[1] + 1, _SCAMP_VERSION[2])))

    def test_minor_version_smaller(self):
        self.assertFalse(BaseTransceiver._is_scamp_version_compabible((
            _SCAMP_VERSION[0], _SCAMP_VERSION[1] - 1, _SCAMP_VERSION[2])))

    def test_patch_version_bigger(self):
        self.assertTrue(BaseTransceiver._is_scamp_version_compabible((
            _SCAMP_VERSION[0], _SCAMP_VERSION[1], _SCAMP_VERSION[2] + 1)))

    def test_patch_version_smaller(self):
        self.assertFalse(BaseTransceiver._is_scamp_version_compabible((
            _SCAMP_VERSION[0], _SCAMP_VERSION[1], _SCAMP_VERSION[2] - 1)))

    def test_compare_versions(self):
        spinn_utilities_parts = spinn_utilities.__version__.split('.')
        spinn_machine_parts = spinn_machine.__version__.split('.')
        spinnman_parts = spinnman.__version__.split('.')

        self.assertEqual(spinn_utilities_parts[0], spinnman_parts[0])
        self.assertLessEqual(spinn_utilities_parts[1], spinnman_parts[1])

        self.assertEqual(spinn_machine_parts[0], spinnman_parts[0])
        self.assertLessEqual(spinn_machine_parts[1], spinnman_parts[1])
