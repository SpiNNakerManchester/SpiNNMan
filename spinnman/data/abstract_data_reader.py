from abc import ABCMeta
from abc import abstractmethod
from six import add_metaclass


@add_metaclass(ABCMeta)
class AbstractDataReader(object):

    @classmethod
    def __subclasshook__(cls, othercls):
        """ Checks if all the abstract methods are present on the subclass
        """
        for C in cls.__mro__:
            for key in C.__dict__:
                item = C.__dict__[key]
                if hasattr(item, "__isabstractmethod__"):
                    if not any(key in B.__dict__ for B in othercls.__mro__):
                        return NotImplemented
        return True

    @abstractmethod
    def read(self, n_bytes):
        """ Read a number of bytes from the underlying stream

        :param n_bytes: The number of bytes to read.
        :type n_bytes: int
        :return: The bytes read from the underlying stream.  May be less than\
                    requested.
        :rtype: bytearray
        :raise IOError: If there is an error obtaining the bytes
        """
        pass

    @abstractmethod
    def readinto(self, array):
        """ Read a number of bytes into an array from the underlying stream

        :param array: An array into which the bytes are to be read
        :type array: bytearray
        :return: The number of bytes written in to the array
        :rtype: int
        :raise IOError: If there is an error obtaining the bytes
        """
        pass

    @abstractmethod
    def readall(self):
        """ Read the rest of the bytes from the underlying stream

        :return: The bytes read
        :rtype: bytearray
        :raise IOError: If there is an error obtaining the bytes
        """
        pass
