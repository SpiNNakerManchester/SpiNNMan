from enum import Enum


class DiagnosticFilterDestination(Enum):
    """ Destination flags for the diagnostic filters.
        Note that only one has to match for the counter to be incremented
    """
    LINK_0 = (0, "Destination is link 0")
    LINK_1 = (1, "Destination is link 1")
    LINK_2 = (2, "Destination is link 2")
    LINK_3 = (3, "Destination is link 3")
    LINK_4 = (4, "Destination is link 4")
    LINK_5 = (5, "Destination is link 5")
    LOCAL_MONITOR = (6, "Destination is the local monitor core")
    LOCAL = (7, "Destination is a local core (but not the monitor core)")
    DUMP = (8, "Destination is to dump the packet")

    def __new__(cls, value, doc=""):
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, value, doc=""):
        self._value_ = value
        self.__doc__ = doc
