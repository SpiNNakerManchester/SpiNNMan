from enum import Enum


class SDPFlag(Enum):
    """ SDPFlag for the message
    """
    REPLY_NOT_EXPECTED = (0x07, "Indicates that a reply is not expected")
    REPLY_EXPECTED = (0x87, "Indicates that a reply is expected")
    REPLY_NOT_EXPECTED_NO_P2P = (
        0x07 | 0x20,
        "Indicates that a reply is not expected and packet should not be P2P "
        "routed")
    REPLY_EXPECTED_NO_P2P = (
        0x87 | 0x20,
        "Indicates that a reply is expected and packet should not be P2P "
        "routed")

    def __new__(cls, value, doc=""):
        # pylint: disable=protected-access, unused-argument
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, value, doc=""):
        self._value_ = value
        self.__doc__ = doc
