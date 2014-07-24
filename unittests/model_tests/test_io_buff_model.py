import unittest
from spinnman.model.io_buffer import IOBuffer

class TestingIOBuf(unittest.TestCase):
    def test_new_buf(self):
        iobuf = IOBuffer(0,1,2,'Everything failed on chip.')
        self.assertEqual(iobuf.x, 0)
        self.assertEqual(iobuf.y, 1)
        self.assertEqual(iobuf.p, 2)
        self.assertEqual(iobuf.iobuf, 'Everything failed on chip.')


if __name__ == '__main__':
    unittest.main()
