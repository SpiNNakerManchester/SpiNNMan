from enum import Enum


class SCPResult(Enum):
    """ The SCP Result codes
    """
    RC_OK = (0x80, "SCPCommand completed OK")
    RC_LEN = (0x81, "Bad packet length")
    RC_SUM = (0x82, "Bad checksum")
    RC_CMD = (0x83, "Bad/invalid command")
    RC_ARG = (0x84, "Invalid arguments")
    RC_PORT = (0x85, "Bad port number")
    RC_TIMEOUT = (0x86, "Timeout")
    RC_ROUTE = (0x87, "No P2P route")
    RC_CPU = (0x88, "Bad CPU number")
    RC_DEAD = (0x89, "SHM destination dead")
    RC_BUF = (0x8a, "No free Shared Memory buffers")
    RC_P2P_NOREPLY = (0x8b, "No reply to open")
    RC_P2P_REJECT = (0x8c, "Open rejected")
    RC_P2P_BUSY = (0x8d, "Destination busy")
    RC_P2P_TIMEOUT = (0x8e, "Dest did not respond")
    RC_PKT_TX = (0x8f, "Pkt Transmission failed")

    def __new__(cls, value, doc=""):
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, value, doc=""):
        self._value_ = value
        self.__doc__ = doc
