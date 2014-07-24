import unittest
from spinnman.messages.scp.scp_response_header import SCPResponseHeader, SCPResult
import struct
from spinnman.data.little_endian_byte_array_byte_reader import LittleEndianByteArrayByteReader
from spinnman.exceptions import SpinnmanInvalidParameterException,\
    SpinnmanInvalidPacketException

class TestSCPResponseHeader(unittest.TestCase):
    def test_new_scp_response_header(self):
        scp_response = SCPResponseHeader()
        self.assertEqual(scp_response.result, None)
        self.assertEqual(scp_response.sequence, None)

    def test_ok_response(self):
        scp_response = SCPResponseHeader()
        result = SCPResult.RC_OK.value
        seq = 103
        byte_stream = struct.pack('<HH',result,seq)
        byte_stream = LittleEndianByteArrayByteReader(bytearray(byte_stream))
        scp_response.read_scp_response_header(byte_stream)
        self.assertEqual(scp_response.result, SCPResult.RC_OK)
        self.assertEqual(scp_response.sequence, seq)

    def test_err_response(self):
        scp_response = SCPResponseHeader()
        result = SCPResult.RC_OK.value
        seq = 103
        byte_stream = struct.pack('<HH',result,seq)
        byte_stream = LittleEndianByteArrayByteReader(bytearray(byte_stream))
        scp_response.read_scp_response_header(byte_stream)
        self.assertEqual(scp_response.result, SCPResult.RC_OK)
        self.assertEqual(scp_response.sequence, seq)

    def test_invalid_size_response(self):
        with self.assertRaises(SpinnmanInvalidPacketException):
            scp_response = SCPResponseHeader()
            result = SCPResult.RC_OK.value
            seq = 103
            byte_stream = struct.pack('<H',result)
            byte_stream = LittleEndianByteArrayByteReader(bytearray(byte_stream))
            scp_response.read_scp_response_header(byte_stream)

    def test_invalid_result(self):
        with self.assertRaises(SpinnmanInvalidParameterException):
            scp_response = SCPResponseHeader()
            result = 100
            seq = 103
            byte_stream = struct.pack('<HH',result,seq)
            byte_stream = LittleEndianByteArrayByteReader(bytearray(byte_stream))
            scp_response.read_scp_response_header(byte_stream)


if __name__ == '__main__':
    unittest.main()
