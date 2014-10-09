from spinnman.messages.eidio.abstract_eidio_message import AbstractEIDIOMessage


class EIDIOMessage(AbstractEIDIOMessage):

    def __init__(self, eidio_header, data):
        AbstractEIDIOMessage.__init__(self, data)
        self._eidio_header = eidio_header

    @property
    def eidio_header(self):
        return self._eidio_header
    
    def is_EIDIO_message(self):
        return True