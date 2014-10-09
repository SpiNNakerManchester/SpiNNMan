from spinnman.messages.eidio.abstract_eidio_message import AbstractEIDIOMessage


class EIDIOCommandMessage(AbstractEIDIOMessage):

    def __init__(self, eidio_command_header, data):
        AbstractEIDIOMessage.__init__(self, data)
        self._eidio_command_header = eidio_command_header

    @property
    def eidio_header(self):
        return self._eidio_command_header

    def is_EIDIO_message(self):
        return True