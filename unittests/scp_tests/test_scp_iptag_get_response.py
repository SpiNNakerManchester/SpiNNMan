import unittest
# from struct import pack


class MyTestCase(unittest.TestCase):
    @unittest.skip("Test not implemented yet")
    def test_something(self):
        self.assertEqual(True, False, "Test not implemented yet")


if __name__ == '__main__':
    unittest.main()
