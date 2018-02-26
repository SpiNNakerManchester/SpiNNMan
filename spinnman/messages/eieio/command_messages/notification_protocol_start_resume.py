from .eieio_command_message import EIEIOCommandMessage
from .eieio_command_header import EIEIOCommandHeader
from spinnman.constants import EIEIO_COMMAND_IDS


class NotificationProtocolStartResume(EIEIOCommandMessage):
    """ Packet which indicates that the toolchain has started or resumed
    """
    __slots__ = []

    def __init__(self):
        super(NotificationProtocolStartResume, self).__init__(
            EIEIOCommandHeader(
                EIEIO_COMMAND_IDS.START_RESUME_NOTIFICATION))

    @staticmethod
    def from_bytestring(command_header, data, offset):
        return NotificationProtocolStartResume()
