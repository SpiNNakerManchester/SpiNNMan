from enum import Enum


class EIEIOType(Enum):
    """ Possible types of EIEIO packets
    """
    KEY_16_BIT = (0, 2, 0, "Indicates that data is keys which are 16 bits")
    KEY_PAYLOAD_16_BIT = (
        1, 2, 2, "Indicates that data is keys and payloads of 16 bits")
    KEY_32_BIT = (2, 4, 0, "Indicates that data is keys of 32 bits")
    KEY_PAYLOAD_32_BIT = (
        3, 4, 4, "Indicates that data is keys and payloads of 32 bits")

    def __new__(cls, value, key_bytes, payload_bytes, doc=""):
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, value, key_bytes, payload_bytes, doc=""):
        self._value_ = value
        self._key_bytes = key_bytes
        self._payload_bytes = payload_bytes
        self.__doc__ = doc

    @property
    def key_bytes(self):
        """ The number of bytes used by each key element

        :rtype: int
        """
        return self._key_bytes

    @property
    def payload_bytes(self):
        """ The number of bytes used by each payload element

        :rtype: int
        """
        return self._payload_bytes

    @property
    def max_value(self):
        """ The maximum value of the key or payload (if there is a payload)

        :rtype: int
        """
        return (1 << (self._key_bytes * 8)) - 1
