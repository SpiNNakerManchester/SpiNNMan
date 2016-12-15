from enum import Enum


class DiagnosticFilterEmergencyRoutingStatus(Enum):
    """ Emergency routing status flags for the diagnostic filters.
        Note that only one has to match for the counter to be incremented
    """
    NORMAL = (0, "Packet is not emergency routed")
    FIRST_STAGE_COMBINED = (1, "Packet is in first hop of emergency route;"
                               " packet should also have been sent here by"
                               " normal routing")
    FIRST_STAGE = (2, "Packet is in first hop of emergency route; packet"
                      " wouldn't have reached this router without emergency"
                      " routing")
    SECOND_STAGE = (3, "Packet is in last hop of emergency route and should"
                       " now return to normal routing")

    def __new__(cls, value, doc=""):
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, value, doc=""):
        self._value_ = value
        self.__doc__ = doc
