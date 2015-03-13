
from abc import ABCMeta
from abc import abstractmethod
from six import add_metaclass

@add_metaclass(ABCMeta)
class AbstractEIEIOMessage(object):

    def __init__(self, data):
        self._data = data

    @property
    def data(self):
        """ The data in the packet

        :return: The data
        :rtype: bytearray
        """
        return self._data

    @abstractmethod
    def is_EIEIO_message(self):
        """ the extra method for is instance to work

        :return:
        """
