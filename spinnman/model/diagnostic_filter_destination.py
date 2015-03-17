from enum import Enum


class DiagnosticFilterDestination(Enum):
    """ Destination flags for the diagnostic filters.
        Note that only one has to match for the counter to be incremented
    """
    DUMP = (0, "Destination is to dump the packet")
    LOCAL = (1, "Destination is a local core (but not the monitor core)")
    LOCAL_MONITOR = (2, "Destination is the local monitor core")
    LINK_0 = (3, "Destination is link 0")
    LINK_1 = (4, "Destination is link 1")
    LINK_2 = (5, "Destination is link 2")
    LINK_3 = (6, "Destination is link 3")
    LINK_4 = (7, "Destination is link 4")
    LINK_5 = (8, "Destination is link 5")

    def __new__(cls, value, doc=""):
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, value, doc=""):
        self._value_ = value
        self.__doc__ = doc
