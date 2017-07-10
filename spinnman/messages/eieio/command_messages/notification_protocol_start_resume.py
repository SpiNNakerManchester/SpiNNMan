from .eieio_command_message import EIEIOCommandMessage
from .eieio_command_header import EIEIOCommandHeader
from spinnman.constants import EIEIO_COMMAND_IDS


class NotificationProtocolStartResume(EIEIOCommandMessage):
    """ Packet which indicates that the toolchain has started or resumed
    """
    def __init__(self):
        EIEIOCommandMessage.__init__(
            self, EIEIOCommandHeader(
                EIEIO_COMMAND_IDS.START_RESUME_NOTIFICATION.value))

    @property
    def bytestring(self):
        data = super(NotificationProtocolStartResume, self).bytestring
        return data

    @staticmethod
    def from_bytestring(command_header, data, offset):
        return NotificationProtocolStartResume()
