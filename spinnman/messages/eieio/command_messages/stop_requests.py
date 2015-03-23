from spinnman.messages.eieio.command_messages.eieio_command_message\
    import EIEIOCommandMessage
from spinnman import constants


class StopRequests(EIEIOCommandMessage):

    def __init__(self):
        EIEIOCommandMessage.__init__(
            self, constants.EIEIO_COMMAND_IDS.STOP_SENDING_REQUESTS.value)
