from enum import Enum


class SCPSignal(Enum):
    """ SCP Signals
    """
    INITIALISE = (0, 2)
    POWER_DOWN = (1, 2)
    STOP = (2, 2)
    START = (3, 2)
    SYNC0 = (4, 0)
    SYNC1 = (5, 0)
    PAUSE = (6, 0)
    CONTINUE = (7, 0)
    EXIT = (8, 2)
    TIMER = (9, 0)
    USER_0 = (10, 0)
    USER_1 = (11, 0)
    USER_2 = (12, 0)
    USER_3 = (13, 0)

    def __new__(cls, value, signal_type, doc=""):
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, value, signal_type, doc=""):
        """

        :param value: The value used for the signal
        :type value: int
        :param signal_type: The "type" of the signal, between 0 and 2
        :type signal_type: int
        """
        self._value_ = value
        self._signal_type = signal_type
        self.__doc__ = doc

    @property
    def signal_type(self):
        return self._signal_type
