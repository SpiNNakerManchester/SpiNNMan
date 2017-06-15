import unittest
from spinnman.model import MachineDimensions


class TestMachineDimensionsModel(unittest.TestCase):

    def test_new_iptag(self):
        x_max = 253
        y_max = 220
        machine_dim = MachineDimensions(x_max, y_max)
        self.assertEqual(x_max, machine_dim.width)
        self.assertEqual(y_max, machine_dim.height)


if __name__ == '__main__':
    unittest.main()
