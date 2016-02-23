import unittest

from spinn_storage_handlers.abstract_classes.abstract_data_reader \
    import AbstractDataReader
from spinn_storage_handlers.little_endian_data_reader_byte_reader import \
    LittleEndianDataReaderByteReader


class MyDataReader(AbstractDataReader):
    def __init__(self, data_stream):
        self._data_stream = data_stream
        self._index = 0

    def read(self, n_bytes):
        list_of_bytes = list()
        for i in range(n_bytes):
            if self._index < len(self._data_stream):
                list_of_bytes.append(self._data_stream[self._index])
                self._index += 1
        return list_of_bytes

    def readinto(self, array):
        pass

    def readall(self):
        list_of_bytes = list()
        while self._index < len(self._data_stream):
            list_of_bytes.append(self._data_stream[self._index])
            self._index += 1
        return list_of_bytes

class TestLittleEndianDataReader(unittest.TestCase):
    def test_read_byte(self):
        reader = LittleEndianDataReaderByteReader(MyDataReader(bytearray([1, 2, 3, 4, 5])))
        self.assertEqual(reader.read_byte(),1)
        self.assertEqual(reader.read_byte(),2)
        self.assertEqual(reader.read_byte(),3)
        self.assertEqual(reader.read_byte(),4)
        self.assertEqual(reader.read_byte(),5)
        with self.assertRaises(EOFError):
            reader.read_byte()

    def test_read_bytes(self):
        ba = bytearray([1, 2, 3, 4, 5])
        reader = LittleEndianDataReaderByteReader(MyDataReader(ba))
        stream = reader.read_bytes(5)
        for i in range(5):
            self.assertEqual(stream[i],ba[i])

    def test_read_bytes_error(self):
        with self.assertRaises(EOFError):
            reader = LittleEndianDataReaderByteReader(MyDataReader(bytearray([1, 2, 3, 4, 5])))
            reader.read_bytes(6)

    def test_read_short(self):
        reader = LittleEndianDataReaderByteReader(MyDataReader(bytearray([0xF1,0xF2])))
        self.assertEqual(reader.read_short(),0xF2F1)

    def test_read_short_not_enough_bytes(self):
        with self.assertRaises(EOFError):
            reader = LittleEndianDataReaderByteReader(MyDataReader(bytearray([0xF2])))
            reader.read_short()

    def test_read_int(self):
        reader = LittleEndianDataReaderByteReader(MyDataReader(bytearray([0xF1, 0xF2, 0xF3, 0xF4])))
        self.assertEqual(reader.read_int(),0xF4F3F2F1)

    def test_read_int_not_enough_bytes(self):
        with self.assertRaises(EOFError):
            reader = LittleEndianDataReaderByteReader(MyDataReader(bytearray([0xF1, 0xF2, 0xF3])))
            reader.read_int()

    def test_read_long(self):
        reader = LittleEndianDataReaderByteReader(MyDataReader(bytearray([0xF1, 0xF2, 0xF3, 0xF4, 0xF5, 0xF6, 0xF7, 0xF8])))
        self.assertEqual(reader.read_long(),0xF8F7F6F5F4F3F2F1)

    def test_read_long_not_enough_bytes(self):
        with self.assertRaises(EOFError):
            reader = LittleEndianDataReaderByteReader(MyDataReader(bytearray([0xF1, 0xF2, 0xF3, 0xF4, 0xF5, 0xF6, 0xF7])))
            reader.read_long()


if __name__ == '__main__':
    unittest.main()
