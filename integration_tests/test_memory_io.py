from spinnman.utilities.io.memory_io import MemoryIO
import numpy
import os
import struct


class _MockTransceiver(object):

    def __init__(self):
        self._data = dict()

    def _get_memory(self, x, y):
        if (x, y) not in self._data:
            self._data[(x, y)] = numpy.zeros(128 * 1024 * 1024, dtype="uint8")
        return self._data[(x, y)]

    def write_memory(self, x, y, address, data, n_bytes=None):
        memory = self._get_memory(x, y)
        if isinstance(data, int):
            memory[address:address + 4] = numpy.array(
                [data], dtype="uint32").view(dtype="uint8")
        else:
            if n_bytes is None:
                n_bytes = len(data)
            numpy_data = numpy.frombuffer(data[:n_bytes], dtype="uint8")
            memory[address:address + n_bytes] = numpy_data

    def read_memory(self, x, y, address, n_bytes):
        memory = self._get_memory(x, y)
        return bytearray(memory[address:address + n_bytes])

    def fill_memory(
            self, x, y, address, repeat_value, bytes_to_fill, data_type):
        memory = self._get_memory(x, y)
        data_to_fill = numpy.array([repeat_value], dtype="uint{}".format(
            data_type.value * 8)).view("uint8")
        data_to_write = numpy.tile(
            data_to_fill, bytes_to_fill / data_type.value)
        memory[address:address + bytes_to_fill] = data_to_write


def test_memory_io():
    n_bytes = 1000
    read_start_offset = 5
    read_end_offset = -10
    transceiver = _MockTransceiver()
    address = 0
    data = bytearray(numpy.random.randint(0, 256, n_bytes).astype("uint8"))
    memory = MemoryIO(transceiver, 0, 0, address, address + n_bytes)
    memory.write(bytes(data))
    read_memory = memory[read_start_offset:read_end_offset]
    read_data = bytearray(read_memory.read())
    compare_data = data[read_start_offset:read_end_offset]
    assert(compare_data == read_data)

    memory.seek(20)
    test_data = bytearray(list(range(10)))
    memory.write(bytes(test_data))
    memory.write(bytes(test_data))
    memory.seek(-10, os.SEEK_CUR)
    read_data = bytearray(memory.read(10))
    assert(test_data == read_data)

    _test_fill(memory, 100)
    _test_fill(memory, 101)
    _test_fill(memory, 102)
    _test_fill(memory, 103)

    memory.seek(0)
    sub_memory_1 = memory[0:10]
    sub_memory_2 = memory[0:10]
    sub_memory_1.write(b'test')
    result = sub_memory_2.read(4)
    assert(result == b'test')


def _test_fill(memory, offset):
    memory.seek(offset + 12)
    memory.write(struct.pack("B", 10))
    memory[offset:offset + 12].fill(5)
    memory.seek(offset)
    test_data = struct.unpack("<III", memory.read(12))
    assert(test_data == (5, 5, 5))
    assert(struct.unpack("B", memory.read(1))[0] == 10)
