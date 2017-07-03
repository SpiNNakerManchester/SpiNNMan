from enum import Enum


class IPTagCommand(Enum):
    """ SCP IPTag Commands
    """
    NEW = 0
    SET = 1
    GET = 2
    CLR = 3
    TTO = 4

    def __new__(cls, value, doc=""):
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, value, doc=""):
        self._value_ = value
        self.__doc__ = doc
