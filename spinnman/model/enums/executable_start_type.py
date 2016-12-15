from enum import Enum


class ExecutableStartType(Enum):
    """ supports starting of different types of executables
    """

    RUNNING = (0, "does not have a barrierisation requirement")
    SYNC = (1, "requires a barrierisation step")
    USES_SIMULATION_INTERFACE = (
        2, "Supports sync interface, as well as simulation.c interface")

    def __new__(cls, value, doc=""):
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, value, doc=""):
        self._value_ = value
        self.__doc__ = doc
