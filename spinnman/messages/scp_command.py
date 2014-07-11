from enum import Enum


class SCPCommand(Enum):
    """ The SCP Commands and Response codes
    """
    CMD_VER = (0, "Get SCAMP Version")
    CMD_RUN = 1
    CMD_READ = (2, "Read SDRAM")
    CMD_WRITE = (3, "Write SDRAM")
    CMD_APLX = 4
    CMD_FILL = 5
    CMD_REMAP = 16
    CMD_LINK_READ = (17, "Read chip link information")
    CMD_LINK_WRITE = 18
    CMD_AR = 19
    CMD_NNP = (20, "Send a Nearest-Neighbour packet")
    CMD_P2PC = 21
    CMD_SIG = (22, "Send a Signal")
    CMD_FFD = (23, "Send Flood-Fill Data")
    CMD_AS = 24
    CMD_LED = (25, "Control the LEDs")
    CMD_IPTAG = (26, "Set an IPTAG")
    CMD_SROM = 27
    CMD_FLASH_COPY = 49
    CMD_FLASH_ERASE = 50
    CMD_FLASH_WRITE = 51
    CMD_RESET = 55
    CMD_POWER = 57
    CMD_TUBE = 64
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
