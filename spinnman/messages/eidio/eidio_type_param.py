from enum import Enum


class EIDIOTypeParam(Enum):
    """ eidio type Flag for the message
    """
    KEY_16_BIT = (0, "Indicates that data is keys which are 16 bits")
    KEY_PAYLOAD_16_BIT = (1, "Indicates that data is keys and payloads of 16 bits")
    KEY_32_BIT = (2, "Indicates that data is keys of 32 bits")
    KEY_PAYLOADS_32_BIT = (3, "Indicates that data is keys and payloads of 32 bits")

    def __new__(cls, value, doc=""):
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, value, doc=""):
        self._value_ = value
        self.__doc__ = doc

