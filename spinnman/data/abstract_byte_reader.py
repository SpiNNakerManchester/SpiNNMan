from abc import ABCMeta
from abc import abstractmethod
from six import add_metaclass


@add_metaclass(ABCMeta)
class AbstractByteReader(object):
    """ An abstract reader of bytes.  Note that due to endianness concerns,\
        the methods of this reader should be used directly for the appropriate\
        data type being read; e.g. an int should be written using read_int\
        rather than calling read_byte 4 times unless a specific endianness is\
        being achieved.
    """

    @abstractmethod
    def is_at_end(self):
        """ returns true if the reader is currently at the end of the byte
        reader

        :return: returns true if the reader is currently at the end of the byte
        reader false otherwise
        :rtype: bool
        """

    @abstractmethod
    def read_byte(self):
        """ Reads the next byte

        :return: A byte
        :rtype: int
        :raise IOError: If there is an error reading from the stream
        :raise EOFError: If there are no more bytes to read
        """
        pass

    def read_bytes(self, size=None):
        """ Reads an array of bytes

        :param size: The number of bytes to read, or None to read all of the\
                    remaining bytes
        :type size: int
        :return: An array of bytes
        :rtype: bytearray
        :raise IOError: If there is an error reading from the stream
        :raise EOFError: If there are too few bytes to read the requested\
                    size.  Note that if there are no more bytes and size is\
                    None, an empty array will be returned
        """
        pass

    @abstractmethod
    def read_short(self):
        """ Reads the next two bytes as a short value

        :return: A short
        :rtype: int
        :raise IOError: If there is an error reading from the stream
        :raise EOFError: If there are too few bytes to read a short
        """
        pass

    @abstractmethod
    def read_int(self):
        """ Read the next four bytes as in int value

        :return: An int
        :rtype: int
        :raise IOError: If there is an error reading from the stream
        :raise EOFError: If there are too few bytes to read an int
        """
        pass

    @abstractmethod
    def read_long(self):
        """ Reads the next eight bytes as a long value

        :return: A long
        :rtype: long
        :raise IOError: If there is an error reading from the stream
        :raise EOFError: If there are too few bytes to read a long
        """
        pass
