from enum import Enum


class DiagnosticFilterPayloadStatus(Enum):
    """ Payload flags for the diagnostic filters.
        Note that only one has to match for the counter to be incremented
    """
    WITH_PAYLOAD = (0, "Packet has a payload")
    WITHOUT_PAYLOAD = (1, "Packet doesn't have a payload")

    def __new__(cls, value, doc=""):
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, value, doc=""):
        self._value_ = value
        self.__doc__ = doc
