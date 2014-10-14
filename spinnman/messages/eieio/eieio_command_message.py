from spinnman.messages.eieio.abstract_eieio_message import AbstractEIEIOMessage


class EIEIOCommandMessage(AbstractEIEIOMessage):

    def __init__(self, eieio_command_header, data):
        AbstractEIEIOMessage.__init__(self, data)
        self._eieio_command_header = eieio_command_header

    @property
    def eieio_header(self):
        return self._eieio_command_header

    def is_EIEIO_message(self):
        return True

