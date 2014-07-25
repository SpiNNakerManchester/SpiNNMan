import unittest
from spinnman.data.file_data_reader import FileDataReader
from spinnman.data.abstract_data_reader import AbstractDataReader


class TestFileDataReader(unittest.TestCase):
    def setUp(self):
        self.reader = None

    def tearDown(self):
        if self.reader is not None:
            self.reader.close()

    def test_read_one_byte(self):
        self.reader = FileDataReader('file_data/txt_one_byte')
        stream = self.reader.read(1)
        self.assertEqual(stream[0],ord('1'))

    def test_readinto_one_byte(self):
        self.reader = FileDataReader('file_data/txt_one_byte')
        ba = bytearray(1)
        stream = self.reader.readinto(ba)
        self.assertEqual(len(ba),1)
        self.assertEqual(ba[0],ord('1'))

    def test_read_five_byte(self):
        self.reader = FileDataReader('file_data/txt_5_bytes')
        stream = self.reader.read(5)
        self.assertEqual(len(stream),5)
        self.assertEqual(stream[0],ord('1'))
        self.assertEqual(stream[1],ord('2'))
        self.assertEqual(stream[2],ord('3'))
        self.assertEqual(stream[3],ord('4'))
        self.assertEqual(stream[4],ord('5'))

    def test_read_from_empty_file(self):
        self.reader = FileDataReader('file_data/txt_empty')
        stream = self.reader.read(1)
        self.assertEqual(len(stream),0)

    def test_read_truncate(self):
        self.reader = FileDataReader('file_data/txt_one_byte_from_multiple_bytes')
        stream = self.reader.read(2)
        self.assertEqual(len(stream),2)
        self.assertEqual(stream[0],240)
        self.assertEqual(stream[1],164)



if __name__ == '__main__':
    unittest.main()
