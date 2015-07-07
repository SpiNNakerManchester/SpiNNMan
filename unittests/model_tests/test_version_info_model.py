import unittest
from spinnman.model.version_info import VersionInfo
import struct
from spinnman.exceptions import SpinnmanInvalidParameterException

class TestVersionInfo(unittest.TestCase):
    def test_retrieving_bits_from_version_data(self):
        p2p_adr = 0xf0a1
        phys_cpu = 0xff
        virt_cpu = 0x3b
        ver_number = 0xff
        arg1 = ((p2p_adr << 16) | (phys_cpu << 8) | virt_cpu)
        buffer_size = 0x10
        arg2 = ((ver_number << 16) | buffer_size)
        build_date = 0x1000
        arg3 = build_date
        data = "my/spinnaker"

        version_data = struct.pack('<III13s',arg1,arg2,arg3,data)
        version_data = bytearray(version_data)
        vi = VersionInfo(version_data, 0)
        self.assertEqual(vi.name,'my')
        self.assertEqual(vi.version_number,ver_number/100.0)
        self.assertEqual(vi.hardware,'spinnaker')
        self.assertEqual(vi.x,0xf0)
        self.assertEqual(vi.y,0xa1)
        self.assertEqual(vi.p,0x3b)
        self.assertEqual(vi.build_date,build_date)
        self.assertEqual(vi.version_string,data)

    def test_retrieving_bits_from_invalid_version_data_format(self):
        with self.assertRaises(SpinnmanInvalidParameterException):
            p2p_adr = 0xf0a1
            phys_cpu = 0xff
            virt_cpu = 0x3b
            ver_number = 0xff
            arg1 = ((p2p_adr << 16) | (phys_cpu << 8) | virt_cpu)
            buffer_size = 0x10
            arg2 = ((ver_number << 16) | buffer_size)
            build_date = 0x1000
            arg3 = build_date
            data = "my.spinnaker"

            version_data = struct.pack('<III13s',arg1,arg2,arg3,data)
            version_data = bytearray(version_data)
            vi = VersionInfo(version_data, 0)

    def test_retrieving_bits_from_invalid_sized_version_data(self):
        with self.assertRaises(SpinnmanInvalidParameterException):
            p2p_adr = 0xf0a1
            phys_cpu = 0xff
            virt_cpu = 0x3b
            ver_number = 0xff
            arg1 = ((p2p_adr << 16) | (phys_cpu << 8) | virt_cpu)
            buffer_size = 0x10
            arg2 = ((ver_number << 16) | buffer_size)
            build_date = 0x1000
            arg3 = build_date
            data = "my/spinnaker"

            version_data = struct.pack('<II13s',arg1,arg2,data)
            version_data = bytearray(version_data)
            vi = VersionInfo(version_data, 0)


if __name__ == '__main__':
    unittest.main()
