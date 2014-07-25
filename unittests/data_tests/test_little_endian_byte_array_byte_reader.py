import unittest
from spinnman.data.little_endian_byte_array_byte_reader import LittleEndianByteArrayByteReader
from struct import pack

class TestLittleEndianByteArrayByteReader(unittest.TestCase):
    def test_new_empty_reader(self):
        LittleEndianByteArrayByteReader(None)

    def test_read_byte(self):
        byte_stream = pack('<B',1)
        byte_stream = bytearray(byte_stream)
        reader = LittleEndianByteArrayByteReader(byte_stream)
        self.assertEqual(reader.read_byte(),1)

    def test_read_bytes(self):
        byte_stream = pack('<BBB',1,2,3)
        byte_stream = bytearray(byte_stream)
        reader = LittleEndianByteArrayByteReader(byte_stream)
        value = reader.read_bytes()
        for i in range(3):
            self.assertEqual(value[i],i+1)

    def test_read_bytes_not_enough_bits(self):
        with self.assertRaises(EOFError):
            byte_stream = pack('<BBB',1,2,3)
            byte_stream = bytearray(byte_stream)
            reader = LittleEndianByteArrayByteReader(byte_stream)
            value = reader.read_bytes(4)

    def test_read_short(self):
        byte_stream = pack('<H',0x87)
        byte_stream = bytearray(byte_stream)
        reader = LittleEndianByteArrayByteReader(byte_stream)
        value = reader.read_short()
        self.assertEqual(value,0x87)

    def test_read_short_not_enough_bits(self):
        with self.assertRaises(EOFError):
            byte_stream = pack('<B',3)
            byte_stream = bytearray(byte_stream)
            reader = LittleEndianByteArrayByteReader(byte_stream)
            value = reader.read_short()

    def test_read_int(self):
        byte_stream = pack('<I',0xFF12)
        byte_stream = bytearray(byte_stream)
        reader = LittleEndianByteArrayByteReader(byte_stream)
        value = reader.read_int()
        self.assertEqual(value,0xFF12)

    def test_read_int_not_enough_bits(self):
        with self.assertRaises(EOFError):
            byte_stream = pack('<H',3)
            byte_stream = bytearray(byte_stream)
            reader = LittleEndianByteArrayByteReader(byte_stream)
            value = reader.read_int()

    def test_read_long(self):
        byte_stream = pack('<Q',0xFF1200A3)
        byte_stream = bytearray(byte_stream)
        reader = LittleEndianByteArrayByteReader(byte_stream)
        value = reader.read_long()
        self.assertEqual(value,0xFF1200A3)

    def test_read_long_not_enough_bits(self):
        with self.assertRaises(EOFError):
            byte_stream = pack('<I',10)
            byte_stream = bytearray(byte_stream)
            reader = LittleEndianByteArrayByteReader(byte_stream)
            value = reader.read_long()

if __name__ == '__main__':
    unittest.main()
