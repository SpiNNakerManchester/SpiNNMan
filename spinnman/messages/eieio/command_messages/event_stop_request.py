from spinnman.constants import EIEIO_COMMAND_IDS
from .eieio_command_message import EIEIOCommandMessage
from .eieio_command_header import EIEIOCommandHeader


class EventStopRequest(EIEIOCommandMessage):
    """ Packet used for the buffering input technique which causes the parser\
        of the input packet to terminate its execution
    """
    def __init__(self):
        EIEIOCommandMessage.__init__(
            self, EIEIOCommandHeader(EIEIO_COMMAND_IDS.EVENT_STOP.value))
