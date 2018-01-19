from .eieio_command_message import EIEIOCommandMessage
from .eieio_command_header import EIEIOCommandHeader
from spinnman.constants import EIEIO_COMMAND_IDS


class StartRequests(EIEIOCommandMessage):
    """ Packet used in the context of buffering input for the host computer to\
        signal to the SpiNNaker system that, if needed, it is possible to\
        send more "SpinnakerRequestBuffers" packet
    """
    __slots__ = []

    def __init__(self):
        super(StartRequests, self).__init__(EIEIOCommandHeader(
            EIEIO_COMMAND_IDS.START_SENDING_REQUESTS))
