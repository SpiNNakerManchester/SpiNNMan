from spinnman import constants
from spinnman.messages.eieio.command_messages.eieio_command_message\
    import EIEIOCommandMessage
from spinnman.messages.eieio.command_messages.eieio_command_header\
    import EIEIOCommandHeader


class PaddingRequest(EIEIOCommandMessage):

    def __init__(self):
        EIEIOCommandMessage.__init__(
            self, EIEIOCommandHeader(
                constants.EIEIO_COMMAND_IDS.EVENT_PADDING.value))

    @staticmethod
    def get_min_packet_length():
        return 2
