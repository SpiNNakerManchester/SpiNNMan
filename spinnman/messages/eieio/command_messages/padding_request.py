from spinnman.constants import EIEIO_COMMAND_IDS
from .eieio_command_message import EIEIOCommandMessage
from .eieio_command_header import EIEIOCommandHeader


class PaddingRequest(EIEIOCommandMessage):
    """ Packet used to pad space in the buffering area, if needed
    """
    __slots__ = []

    def __init__(self):
        super(PaddingRequest, self).__init__(EIEIOCommandHeader(
            EIEIO_COMMAND_IDS.EVENT_PADDING))

    @staticmethod
    def get_min_packet_length():
        return 2
