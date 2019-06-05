import unittest
import spinn_utilities
import spinn_machine
import spinn_storage_handlers
from spinnman.transceiver import Transceiver, _SCAMP_VERSION
import spinnman


class Test(unittest.TestCase):
    """ Tests for the SCAMP version comparison
    """

    def test_version_same(self):
        self.assertTrue(Transceiver.is_scamp_version_compabible((
            _SCAMP_VERSION[0], _SCAMP_VERSION[1], _SCAMP_VERSION[2])))

    def test_major_version_too_big(self):
        self.assertFalse(Transceiver.is_scamp_version_compabible((
            _SCAMP_VERSION[0] + 1, 0, 0)))

    def test_major_version_too_small(self):
        self.assertFalse(Transceiver.is_scamp_version_compabible((
            _SCAMP_VERSION[0] - 1, 0, 0)))

    def test_minor_version_bigger(self):
        self.assertTrue(Transceiver.is_scamp_version_compabible((
            _SCAMP_VERSION[0], _SCAMP_VERSION[1] + 1, _SCAMP_VERSION[2])))

    def test_minor_version_smaller(self):
        self.assertFalse(Transceiver.is_scamp_version_compabible((
            _SCAMP_VERSION[0], _SCAMP_VERSION[1] - 1, _SCAMP_VERSION[2])))

    def test_patch_version_bigger(self):
        self.assertTrue(Transceiver.is_scamp_version_compabible((
            _SCAMP_VERSION[0], _SCAMP_VERSION[1], _SCAMP_VERSION[2] + 1)))

    def test_patch_version_smaller(self):
        self.assertFalse(Transceiver.is_scamp_version_compabible((
            _SCAMP_VERSION[0], _SCAMP_VERSION[1], _SCAMP_VERSION[2] - 1)))

    def test_compare_versions(self):
        spinn_utilities_parts = spinn_utilities.__version__.split('.')
        spinn_machine_parts = spinn_machine.__version__.split('.')
        spinn_storage_handlers_parts = spinn_storage_handlers.__version__.\
            split('.')
        spinnman_parts = spinnman.__version__.split('.')

        self.assertEquals(spinn_utilities_parts[0], spinnman_parts[0])
        self.assertLessEqual(spinn_utilities_parts[1], spinnman_parts[1])

        self.assertEquals(spinn_machine_parts[0], spinnman_parts[0])
        self.assertLessEqual(spinn_machine_parts[1], spinnman_parts[1])

        self.assertEquals(spinn_storage_handlers_parts[0], spinnman_parts[0])
        self.assertLessEqual(spinn_storage_handlers_parts[1],
                             spinnman_parts[1])
