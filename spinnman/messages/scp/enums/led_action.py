from enum import Enum


class LEDAction(Enum):
    """ The SCP LED actions
    """

    TOGGLE = (1, "Toggle the LED status")
    OFF = (2, "Turn the LED off")
    ON = (3, "Turn the LED on")

    def __new__(cls, value, doc=""):
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, value, doc=""):
        self._value_ = value
        self.__doc__ = doc
