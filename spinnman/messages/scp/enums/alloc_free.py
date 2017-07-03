from enum import Enum


class AllocFree(Enum):
    """ The SCP Allocation and Free codes
    """

    ALLOC_SDRAM = (0, "Allocate SDRAM")
    FREE_SDRAM_BY_POINTER = (1, "Free SDRAM using a Pointer")
    FREE_SDRAM_BY_TAG = (2, "Free SDRAM using a Tag")
    ALLOC_ROUTING = (3, "Allocate Routing Entries")
    FREE_ROUTING_BY_POINTER = (4, "Free Routing Entries by Pointer")
    FREE_ROUTING_BY_APP_ID = (5, "Free Routing Entries by APP ID")

    def __new__(cls, value, doc=""):
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, value, doc=""):
        self._value_ = value
        self.__doc__ = doc
