from enum import Enum


class RouterError(Enum):
    """ Router error flags
    """
    ERROR = (0x80000000, "Error packet detected")
    OVERFLOW = (0x40000000, "More than one error packet detected")
    PARITY = (0x20000000, "Parity Error")
    FRAMING = (0x10000000, "Framing Error")
    TIMESTAMP = (0x08000000, "Timestamp Error")

    def __new__(cls, value, doc=""):
        # pylint: disable=protected-access, unused-argument
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, value, doc=""):
        self._value_ = value
        self.__doc__ = doc
