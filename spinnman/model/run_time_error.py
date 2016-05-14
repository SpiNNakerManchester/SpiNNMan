from enum import Enum


class RunTimeError(Enum):
    """ SARK Run time errors
    """
    NONE = 0
    RESET = 1
    UNDEF = 2
    SVC = 3
    PABT = 4
    DABT = 5
    IRQ = 6
    FIQ = 7
    VIC = 8
    ABORT = 9
    MALLOC = 10
    DIVBY0 = 11
    EVENT = 12
    SWERR = 13
    IOBUF = 14
    ENABLE = 15
    NULL = 16
    PKT = 17
    TIMER = 18
    API = 19
    SARK_VERSRION_INCORRECT = 20

    def __new__(cls, value, doc=""):
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, value, doc=""):
        self._value_ = value
        self.__doc__ = doc
