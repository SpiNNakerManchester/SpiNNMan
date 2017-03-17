from enum import Enum


class DiagnosticFilterSource(Enum):
    """ Source flags for the diagnostic filters.
        Note that only one has to match for the counter to be incremented
    """
    LOCAL = (0, "Source is a local core")
    NON_LOCAL = (1, "Source is not a local core")

    def __new__(cls, value, doc=""):
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, value, doc=""):
        self._value_ = value
        self.__doc__ = doc
