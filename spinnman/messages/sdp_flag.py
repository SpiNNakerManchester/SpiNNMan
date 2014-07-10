from enum import Enum


class SDPFlag(Enum):
    """ SDPFlag for the message
    """
    REPLY_NOT_EXPECTED = (0x07, "Indicates that a reply is not expected")
    REPLY_EXPECTED = (0x87, "Indicates that a reply is expected")
    
    def __init__(self, value, doc=""):
        self._value_ = value
        self.__doc__ = doc
