from spinnman.data.abstract_byte_reader import AbstractByteReader


class LittleEndianDataReaderByteReader(AbstractByteReader):
    """ A byte reader that reads from a data reader using little endian\
        notation
    """

    def is_at_end(self):
        """ required from abstract byte reader

        :return:
        """
        raise NotImplementedError

    def __init__(self, data_reader):
        """

        :param data_reader: The data reader to read from
        :type data_reader: :py:class:`spinnman.data.abstract_data_reader.AbstractDataReader`
        """
        self._data_reader = data_reader

    def read_byte(self):
        """ See :py:meth:`spinnman.data.abstract_byte_reader.AbstractByteReader.read_byte`
        """
        data = self._data_reader.read(1)
        if len(data) == 0:
            raise EOFError("Not enough data to read a byte")
        return data[0]

    def read_bytes(self, size=None):
        """ See :py:meth:`spinnman.data.abstract_byte_reader.AbstractByteReader.read_bytes`
        """
        if size is None:
            return bytearray(self._data_reader.readall())

        data = bytearray()
        bytes_read = None
        while bytes_read != 0 and len(data) < size:
            new_data = self._data_reader.read(size - len(data))
            bytes_read = len(new_data)
            data.extend(new_data)

        if len(data) < size:
            raise EOFError("Not enough bytes to read {} bytes".format(size))
        return data

    def read_short(self):
        """ See :py:meth:`spinnman.data.abstract_byte_reader.AbstractByteReader.read_short`
        """
        try:
            value = self.read_byte() | (self.read_byte() << 8)
            return value
        except EOFError:
            raise EOFError("Not enough bytes to read a short")

    def read_int(self):
        """ See :py:meth:`spinnman.data.abstract_byte_reader.AbstractByteReader.read_int`
        """
        try:
            value = (self.read_byte() | (self.read_byte() << 8)
                     | (self.read_byte() << 16) | (self.read_byte() << 24))
            return value
        except EOFError:
            raise EOFError("Not enough bytes to read a short")

    def read_long(self):
        """ See :py:meth:`spinnman.data.abstract_byte_reader.AbstractByteReader.read_long`
        """
        try:
            value = (self.read_byte() | (self.read_byte() << 8)
                     | (self.read_byte() << 16) | (self.read_byte() << 24)
                     | (self.read_byte() << 32) | (self.read_byte() << 40)
                     | (self.read_byte() << 48) | (self.read_byte() << 56))
            return value
        except EOFError:
            raise EOFError("Not enough bytes to read a short")
