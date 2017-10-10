
from .eieio_command_message import EIEIOCommandMessage
from .eieio_command_header import EIEIOCommandHeader
from spinnman.constants import EIEIO_COMMAND_IDS


class NotificationProtocolPauseStop(EIEIOCommandMessage):
    """ Packet which indicates that the toolchain has paused or stopped
    """
    def __init__(self):
        EIEIOCommandMessage.__init__(
            self, EIEIOCommandHeader(
                EIEIO_COMMAND_IDS.STOP_PAUSE_NOTIFICATION.value))

    @property
    def bytestring(self):
        data = super(NotificationProtocolPauseStop, self).bytestring
        return data

    @staticmethod
    def from_bytestring(command_header, data, offset):
        return NotificationProtocolPauseStop()
