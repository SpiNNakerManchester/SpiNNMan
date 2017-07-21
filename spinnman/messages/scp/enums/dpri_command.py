from enum import Enum


class DPRICommand(Enum):
    """ SCP Dropped Packet Reinjection Commands
    """
    SET_ROUTER_TIMEOUT = (0, "Set the WAIT1 timeout of the router")
    SET_ROUTER_EMERGENCY_TIMEOUT = (1, "Set the WAIT2 timeout of the router")
    SET_PACKET_TYPES = (2, "Set the packet types to reinject")
    GET_STATUS = (3, "Get the status of the reinjector")
    RESET_COUNTERS = (4, "Reset the statistics counters")
    EXIT = (5, "Exit the process")

    def __new__(cls, value, doc=""):
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, value, doc=""):
        self._value_ = value
        self.__doc__ = doc
