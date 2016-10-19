import unittest
from spinnman.transceiver import create_transceiver_from_hostname
from spinnman.utilities.io.memory_io import MemoryIO
import numpy
import os
import struct


class TestMemoryIO(unittest.TestCase):

    def test_memory_io(self):
        n_bytes = 1000
        read_start_offset = 5
        read_end_offset = -10
        transceiver = create_transceiver_from_hostname(
            "spinn-10.cs.man.ac.uk", 2)
        transceiver.ensure_board_is_ready()
        address = transceiver.malloc_sdram(0, 0, n_bytes, 30)
        data = bytearray(numpy.random.randint(0, 256, n_bytes).astype("uint8"))
        memory = MemoryIO(transceiver, 0, 0, address, address + n_bytes)
        print "Written", memory.write(bytes(data)), "bytes"
        read_memory = memory[read_start_offset:read_end_offset]
        read_data = bytearray(read_memory.read())
        compare_data = data[read_start_offset:read_end_offset]
        print "Read", len(read_data), "bytes"
        data_str = [hex(val) for val in compare_data]
        read_str = [hex(val) for val in read_data]
        self.assertEqual(
            compare_data, read_data,
            "Written data is not the same as read data:\n    {}\n    {}"
            .format(data_str, read_str))

        memory.seek(20)
        test_data = bytearray(range(10))
        memory.write(bytes(test_data))
        memory.write(bytes(test_data))
        memory.seek(-10, os.SEEK_CUR)
        read_data = bytearray(memory.read(10))
        self.assertEqual(
            test_data, read_data,
            "Written data is not the same as read data:\n    {}\n    {}"
            .format(
                [hex(val) for val in test_data],
                [hex(val) for val in read_data]))

        self._test_fill(memory, 100)
        self._test_fill(memory, 101)
        self._test_fill(memory, 102)
        self._test_fill(memory, 103)

        transceiver.stop_application(30)
        transceiver.close()

    def _test_fill(self, memory, offset):
        memory.seek(offset + 12)
        memory.write(struct.pack("B", 10))
        memory[offset:offset + 12].fill(5)
        memory.seek(offset)
        test_data = struct.unpack("<III", memory.read(12))
        self.assertEqual(
            test_data, (5, 5, 5),
            "Filled data values unexpected: {}".format(test_data))
        self.assertEqual(
            struct.unpack("B", memory.read(1))[0], 10,
            "Fill overwritten value")
