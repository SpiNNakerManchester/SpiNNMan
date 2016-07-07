from enum import Enum


class P2PTableRoute(Enum):
    """ P2P Routing table routes
    """
    EAST = 0b000
    NORTH_EAST = 0b001
    NORTH = 0b010
    WEST = 0b011
    SOUTH_WEST = 0b100
    SOUTH = 0b101
    NONE = (0b110, "No route to this chip")
    MONITOR = (0b111, "Route to the monitor on the current chip")

    def __new__(cls, value, doc=""):
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, value, doc=""):
        self._value_ = value
        self.__doc__ = doc
