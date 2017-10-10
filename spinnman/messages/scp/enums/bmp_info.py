from enum import Enum


class BMPInfo(Enum):
    """ The SCP BMP Information Types
    """

    SERIAL = (0, "Serial information")
    CAN_STATUS = (2, "CAN status information")
    ADC = (3, "ADC information")
    IP_ADDR = (4, "IP Address")

    def __new__(cls, value, doc=""):
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, value, doc=""):
        self._value_ = value
        self.__doc__ = doc
