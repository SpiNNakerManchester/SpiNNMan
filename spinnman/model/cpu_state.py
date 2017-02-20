from enum import Enum


class CPUState(Enum):
    """ SARK CPU States
    """
    DEAD = 0
    POWERED_DOWN = 1
    RUN_TIME_EXCEPTION = 2
    WATCHDOG = 3
    INITIALISING = 4
    READY = 5
    C_MAIN = 6
    RUNNING = 7
    SYNC0 = 8
    SYNC1 = 9
    PAUSED = 10
    FINISHED = 11
    CPU_STATE_12 = 12
    CPU_STATE_13 = 13
    CPU_STATE_14 = 14
    IDLE = 15

    def __new__(cls, value, doc=""):
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, value, doc=""):
        self._value_ = value
        self.__doc__ = doc
