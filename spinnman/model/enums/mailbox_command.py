from enum import Enum


class MailboxCommand(Enum):
    """ Commands sent between an application and the monitor processor
    """

    SHM_IDLE = (0, "The mailbox is idle")
    SHM_MSG = (1, "The mailbox contains an SDP message")
    SHM_NOP = (2, "The mailbox contains a non-operation")
    SHM_SIGNAL = (3, "The mailbox contains a signal")
    SHM_CMD = (4, "The mailbox contains a command")

    def __new__(cls, value, doc=""):
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, value, doc=""):
        self._value_ = value
        self.__doc__ = doc
