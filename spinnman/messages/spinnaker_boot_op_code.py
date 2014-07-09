from enum import Enum

class SpinnakerBootOpCode(Enum):
    """ Boot message Operation Codes
    """
    
    HELLO = 0x41
    FLOOD_FILL_START = 0x1
    FLOOD_FILL_BLOCK = 0x3
    FLOOD_FILL_CONTROL = 0x5
    
    def __init__(self, value, doc=""):
        self._value_ = value
        self.__doc__ = doc
