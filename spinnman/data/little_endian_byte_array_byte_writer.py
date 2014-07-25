from spinnman.data.abstract_byte_writer import AbstractByteWriter


class LittleEndianByteArrayByteWriter(AbstractByteWriter):
    """ A byte writer that writes to a byte array using little endian notation
    """

    def __init__(self):
        """
        """
        self._data = bytearray()

    def write_byte(self, byte_value):
        """ See :py:meth:`spinnman.data.abstract_byte_writer.AbstractByteWriter.write_byte`
        """
        self._data.append(byte_value & 0xFF)

    def write_bytes(self, byte_iterable):
        """ See :py:meth:`spinnman.data.abstract_byte_writer.AbstractByteWriter.write_bytes`
        """
        self._data.extend(byte_iterable)

    def write_short(self, short_value):
        """ See :py:meth:`spinnman.data.abstract_byte_writer.AbstractByteWriter.write_short`
        """
        self._data.append(short_value & 0xFF)
        self._data.append((short_value >> 8) & 0xFF)

    def write_int(self, int_value):
        """ See :py:meth:`spinnman.data.abstract_byte_writer.AbstractByteWriter.write_int`
        """
        self._data.append(int_value & 0xFF)
        self._data.append((int_value >> 8) & 0xFF)
        self._data.append((int_value >> 16) & 0xFF)
        self._data.append((int_value >> 24) & 0xFF)

    def write_long(self, long_value):
        """ See :py:meth:`spinnman.data.abstract_byte_writer.AbstractByteWriter.write_long`
        """
        self._data.append(long_value & 0xFF)
        self._data.append((long_value >> 8) & 0xFF)
        self._data.append((long_value >> 16) & 0xFF)
        self._data.append((long_value >> 24) & 0xFF)
        self._data.append((long_value >> 32) & 0xFF)
        self._data.append((long_value >> 40) & 0xFF)
        self._data.append((long_value >> 48) & 0xFF)
        self._data.append((long_value >> 56) & 0xFF)

    def get_n_bytes_written(self):
        """ See :py:meth:`spinnman.data.abstract_byte_writer.AbstractByteWriter.get_n_bytes_written`
        """
        return len(self._data)

    @property
    def data(self):
        """ The data that was written

        :rtype: bytearray
        """
        return self._data
