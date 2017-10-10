from .eieio_command_message import EIEIOCommandMessage
from .eieio_command_header import EIEIOCommandHeader
from spinnman.constants import EIEIO_COMMAND_IDS


class StopRequests(EIEIOCommandMessage):
    """ Packet used in the context of buffering input for the host computer to\
        signal to the SpiNNaker system that to stop sending\
        "SpinnakerRequestBuffers" packet
    """
    def __init__(self):
        EIEIOCommandMessage.__init__(
            self, EIEIOCommandHeader(
                EIEIO_COMMAND_IDS.STOP_SENDING_REQUESTS.value))
