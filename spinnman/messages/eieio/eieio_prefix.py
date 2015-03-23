from enum import Enum


class EIEIOPrefix(Enum):
    """ Possible prefixing of keys in EIEIO packets
    """
    LOWER_HALF_WORD = (0, "apply prefix on lower half of the word")
    UPPER_HALF_WORD = (1, "apply prefix on top half of the word")

    def __new__(cls, value, doc=""):
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, value, doc=""):
        self._value_ = value
        self.__doc__ = doc
