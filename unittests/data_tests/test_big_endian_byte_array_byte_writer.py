import unittest

from spinn_storage_handlers.big_endian_byte_array_byte_writer import \
    BigEndianByteArrayByteWriter


class TestLittleEndianByteWriter(unittest.TestCase):
    def test_new_empty_writer(self):
        writer = BigEndianByteArrayByteWriter()
        self.assertEqual(writer.get_n_bytes_written(),0)
        self.assertEqual(writer.data,bytearray())

    def test_write_byte(self):
        writer = BigEndianByteArrayByteWriter()
        writer.write_byte(1)
        self.assertEqual(writer.get_n_bytes_written(),1)
        self.assertEqual(writer.data[0],1)

    def test_write_byte_truncate(self):
        writer = BigEndianByteArrayByteWriter()
        writer.write_byte(0xFF37)
        self.assertEqual(writer.get_n_bytes_written(),1)
        self.assertEqual(writer.data[0],0x37)

    def test_write_bytes(self):
        writer = BigEndianByteArrayByteWriter()
        bytes_to_write = [1,2,3,4,5,6]
        writer.write_bytes(bytes_to_write)
        self.assertEqual(writer.get_n_bytes_written(),len(bytes_to_write))
        self.assertEqual(writer.data,bytearray(bytes_to_write))


    def test_write_short(self):
        writer = BigEndianByteArrayByteWriter()
        short_to_write = 0xF1F2
        writer.write_short(short_to_write)
        self.assertEqual(writer.get_n_bytes_written(),2)
        self.assertEqual(writer.data,bytearray([0xF1,0xF2]))

    def test_write_int(self):
        writer = BigEndianByteArrayByteWriter()
        int_to_write = 0xF1F2F3F4
        writer.write_int(int_to_write)
        self.assertEqual(writer.get_n_bytes_written(),4)
        self.assertEqual(writer.data,bytearray([0xF1, 0xF2, 0xF3,0xF4]))

    def test_write_long(self):
        writer = BigEndianByteArrayByteWriter()
        long_to_write = 0xF1F2F3F4F5F6F7F8
        writer.write_long(long_to_write)
        self.assertEqual(writer.get_n_bytes_written(),8)
        self.assertEqual(writer.data,bytearray([0xF1,0xF2, 0xF3, 0xF4, 0xF5, 0xF6, 0xF7,0xF8]))


if __name__ == '__main__':
    unittest.main()