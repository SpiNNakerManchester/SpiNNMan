import unittest
import tempfile
import os

from spinn_storage_handlers import FileDataReader


class TestFileDataReader(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        (os_fd, cls._file_txt_empty) = tempfile.mkstemp(text=False)
        os.close(os_fd)
        (os_fd, cls._file_txt_one_byte) = tempfile.mkstemp(text=False)
        os.write(os_fd, b"1")
        os.close(os_fd)
        (os_fd, cls._file_txt_five_bytes) = tempfile.mkstemp(text=False)
        os.write(os_fd, b"1")
        os.write(os_fd, b"2")
        os.write(os_fd, b"3")
        os.write(os_fd, b"4")
        os.write(os_fd, b"5")
        os.close(os_fd)

    @classmethod
    def tearDownClass(cls):
        try:
            os.remove(cls._file_txt_empty)
        except OSError:
            pass

        try:
            os.remove(cls._file_txt_one_byte)
        except OSError:
            pass

        try:
            os.remove(cls._file_txt_five_bytes)
        except OSError:
            pass

    def setUp(self):
        self.reader = None

    def tearDown(self):
        if self.reader is not None:
            self.reader.close()

    def test_read_one_byte(self):
        self.reader = FileDataReader(self._file_txt_one_byte)
        stream = self.reader.read(1)
        assert stream == b'1'

    def test_readinto_one_byte(self):
        self.reader = FileDataReader(self._file_txt_one_byte)
        ba = bytearray(1)
        stream = self.reader.readinto(ba)
        assert stream is not None
        assert len(ba) == 1
        assert ba[0] == ord('1')

    def test_read_five_byte(self):
        self.reader = FileDataReader(self._file_txt_five_bytes)
        stream = self.reader.read(5)
        assert stream is not None
        assert len(stream) == 5
        assert stream == b'12345'

    def test_read_from_empty_file(self):
        self.reader = FileDataReader(self._file_txt_empty)
        stream = self.reader.read(1)
        assert stream is not None
        assert len(stream) == 0

    def test_read_truncate(self):
        self.reader = FileDataReader(self._file_txt_five_bytes)
        stream = self.reader.read(2)
        assert stream is not None
        assert len(stream) == 2
        assert stream == b'12'


if __name__ == '__main__':
    unittest.main()
