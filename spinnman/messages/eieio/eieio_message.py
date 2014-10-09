from spinnman.messages.eieio.abstract_eieio_message import AbstractEIEIOMessage


class EIEIOMessage(AbstractEIEIOMessage):

    def __init__(self, eieio_header, data):
        AbstractEIEIOMessage.__init__(self, data)
        self._eieio_header = eieio_header

    @property
    def eidio_header(self):
        return self._eieio_header
    
    def is_EIEIO_message(self):
        return True