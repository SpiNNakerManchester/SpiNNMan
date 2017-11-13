from enum import Enum


class DPRICommand(Enum):
    """ SCP Dropped Packet Reinjection Commands
    """

    def __new__(cls, value, doc=""):
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, value, doc=""):
        self._value_ = value
        self.__doc__ = doc
