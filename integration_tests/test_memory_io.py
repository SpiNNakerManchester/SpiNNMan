import unittest
from spinnman.transceiver import create_transceiver_from_hostname
from spinnman.utilities.memory_io import MemoryIO
import numpy
import os


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
        memory = memory[read_start_offset:read_end_offset]
        read_data = bytearray(memory.read())
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
