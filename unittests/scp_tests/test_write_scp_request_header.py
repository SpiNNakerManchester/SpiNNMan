import unittest
from spinnman.messages.scp.scp_request_header import SCPRequestHeader
from spinnman.data.little_endian_byte_array_byte_writer import \
    LittleEndianByteArrayByteWriter
from spinnman.data.little_endian_byte_array_byte_reader import \
    LittleEndianByteArrayByteReader
from spinnman.messages.scp.scp_command import SCPCommand
from spinnman.exceptions import SpinnmanInvalidParameterException

class TestScpRequestHeader(unittest.TestCase):
    def test_assemble_byte_writer(self):
        scp = SCPRequestHeader(SCPCommand.CMD_VER,1)
        self.assertEqual(scp.command, SCPCommand.CMD_VER)
        self.assertEqual(scp.sequence, 1)
        byte_writer = LittleEndianByteArrayByteWriter()
        scp.write_scp_request_header(byte_writer)
        reader = LittleEndianByteArrayByteReader(byte_writer.data)
        self.assertEqual(reader.read_short(),SCPCommand.CMD_VER.value)
        self.assertEqual(reader.read_short(),1)

    def test_assemble_byte_writer_no_command(self):
        with self.assertRaises(SpinnmanInvalidParameterException):
            scp = SCPRequestHeader(None,1)
            byte_writer = LittleEndianByteArrayByteWriter()
            scp.write_scp_request_header(byte_writer)

    def test_assemble_byte_writer_no_sequence(self):
        with self.assertRaises(SpinnmanInvalidParameterException):
            scp = SCPRequestHeader(SCPCommand.CMD_VER)
            byte_writer = LittleEndianByteArrayByteWriter()
            scp.write_scp_request_header(byte_writer)


if __name__ == '__main__':
    unittest.main()
