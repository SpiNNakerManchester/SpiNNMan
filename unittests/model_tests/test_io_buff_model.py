import unittest
from spinnman.model import IOBuffer


class TestingIOBuf(unittest.TestCase):
    def test_new_buf(self):
        iobuf = IOBuffer(0, 1, 2, 'Everything failed on chip.')
        self.assertIsNotNone(iobuf)
        self.assertEquals(iobuf.x, 0)
        self.assertEquals(iobuf.y, 1)
        self.assertEquals(iobuf.p, 2)
        self.assertEquals(iobuf.iobuf, 'Everything failed on chip.')


if __name__ == '__main__':
    unittest.main()
