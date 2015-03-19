from enum import Enum


class DiagnosticFilterDefaultRoutingStatus(Enum):
    """ Default routing flags for the diagnostic filters.
        Note that only one has to match for the counter to be incremented
    """
    DEFAULT_ROUTED = (0, "Packet is to be default routed")
    NON_DEFAULT_ROUTED = (1, "Packet is not to be default routed")

    def __new__(cls, value, doc=""):
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, value, doc=""):
        self._value_ = value
        self.__doc__ = doc
