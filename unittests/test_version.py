import unittest
from spinnman.transceiver import Transceiver
from spinnman.transceiver import _SCAMP_VERSION


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
