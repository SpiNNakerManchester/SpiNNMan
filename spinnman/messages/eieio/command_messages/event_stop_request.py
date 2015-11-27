from spinnman import constants
from spinnman.messages.eieio.command_messages.eieio_command_message\
    import EIEIOCommandMessage
from spinnman.messages.eieio.command_messages.eieio_command_header\
    import EIEIOCommandHeader


class EventStopRequest(EIEIOCommandMessage):
    """ Packet used for the buffering input technique which causes the parser\
        of the input packet to terminate its execution
    """
    def __init__(self):
        EIEIOCommandMessage.__init__(
            self, EIEIOCommandHeader(
                constants.EIEIO_COMMAND_IDS.EVENT_STOP.value))
