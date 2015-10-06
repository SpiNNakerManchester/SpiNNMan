import unittest

import spinnman.utilities.utility_functions as utils


class Testing_utils(unittest.TestCase):
    def test_big_endian_to_int(self):
        hex_string = "FFFF0000"
        hn = hex_string.decode("hex")
        ba = bytearray(hn)
        ba = utils._get_int_from_big_endian_bytearray(ba,0)
        self.assertEqual(ba, 4294901760)

    def test_big_endian_to_short(self):
        hex_string = "FF00FF00"
        hn = hex_string.decode("hex")
        ba = bytearray(hn)
        ba = utils._get_short_from_big_endian_bytearray(ba,0)
        self.assertEqual(ba, 65280)

    def test_int_to_big_endian(self):
        ba = bytearray(4)
        utils.put_int_in_big_endian_byte_array(ba,0,4294901760)
        hex_string = "FFFF0000"
        hn = hex_string.decode("hex")
        ba2 = bytearray(hn)
        self.assertEqual(ba, ba2)

    def test_short_to_big_endian(self):
        ba = bytearray(2)
        utils._put_short_in_big_endian_byte_array(ba,0,65280)
        hex_string = "FF00"
        hn = hex_string.decode("hex")
        ba2 = bytearray(hn)
        self.assertEqual(ba, ba2)

    def test_int_to_b_endian_to_int(self):
        ba = bytearray(4)
        utils.put_int_in_big_endian_byte_array(ba,0,4294901760)
        ba = utils._get_int_from_big_endian_bytearray(ba,0)
        self.assertEqual(ba, 4294901760)

    def test_short_to_b_endian_to_short(self):
        for i in range(65535):
            ba = bytearray(2)
            utils._put_short_in_big_endian_byte_array(ba,0,i)
            ba = utils._get_short_from_big_endian_bytearray(ba,0)
            self.assertEqual(ba, i)

    def test_little_endian_to_int(self):
        hex_string = "FFFF0000"
        hn = hex_string.decode("hex")
        ba = bytearray(hn)
        ba = utils.get_int_from_little_endian_bytearray(ba,0)
        self.assertEqual(ba, 65535)

    def test_little_endian_to_short(self):
        hex_string = "FF00FF00"
        hn = hex_string.decode("hex")
        ba = bytearray(hn)
        ba = utils.get_short_from_little_endian_bytearray(ba,0)
        self.assertEqual(ba, 255)

    def test_int_to_l_endian_to_int(self):
        ba = bytearray(4)
        utils._put_int_in_little_endian_byte_array(ba,0,4294901760)
        ba = utils.get_int_from_little_endian_bytearray(ba,0)
        self.assertEqual(ba, 4294901760)

    def test_short_to_l_endian_to_short(self):
        for i in range(65535):
            ba = bytearray(2)
            utils._put_short_in_little_endian_byte_array(ba,0,i)
            ba = utils.get_short_from_little_endian_bytearray(ba,0)
            self.assertEqual(ba, i)

    def test_int_to_little_endian(self):
        ba = bytearray(4)
        utils._put_int_in_little_endian_byte_array(ba,0,4294901760)
        hex_string = "0000FFFF"
        hn = hex_string.decode("hex")
        ba2 = bytearray(hn)
        self.assertEqual(ba, ba2)

    def test_short_to_little_endian(self):
        ba = bytearray(2)
        utils._put_short_in_little_endian_byte_array(ba,0,65280)
        hex_string = "00FF"
        hn = hex_string.decode("hex")
        ba2 = bytearray(hn)
        self.assertEqual(ba, ba2)

if __name__ == '__main__':
    unittest.main()
