from enum import Enum


class DiagnosticFilterPacketType(Enum):
    """ Packet type flags for the diagnostic filters.
        Note that only one has to match for the counter to be incremented
    """
    MULTICAST = (0, "Packet is multicast")
    POINT_TO_POINT = (1, "Packet is point-to-point")
    NEAREST_NEIGHBOUR = (2, "Packet is nearest-neighbour")
    FIXED_ROUTE = (3, "Packet is fixed-route")

    def __new__(cls, value, doc=""):
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, value, doc=""):
        self._value_ = value
        self.__doc__ = doc
