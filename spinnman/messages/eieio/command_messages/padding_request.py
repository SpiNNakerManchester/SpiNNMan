from spinnman.constants import EIEIO_COMMAND_IDS
from .eieio_command_message import EIEIOCommandMessage
from .eieio_command_header import EIEIOCommandHeader


class PaddingRequest(EIEIOCommandMessage):
    """ Packet used to pad space in the buffering area, if needed
    """
    def __init__(self):
        EIEIOCommandMessage.__init__(
            self, EIEIOCommandHeader(
                EIEIO_COMMAND_IDS.EVENT_PADDING.value))

    @staticmethod
    def get_min_packet_length():
        return 2
