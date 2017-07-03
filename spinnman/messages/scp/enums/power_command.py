from enum import Enum


class PowerCommand(Enum):
    """ The SCP Power Commands
    """

    POWER_OFF = (0, "Power off the machine")
    POWER_ON = (1, "Power on the machine")

    def __new__(cls, value, doc=""):
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, value, doc=""):
        self._value_ = value
        self.__doc__ = doc
