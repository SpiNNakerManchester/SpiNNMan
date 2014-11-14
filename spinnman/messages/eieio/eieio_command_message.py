from spinnman.messages.eieio.abstract_eieio_message import AbstractEIEIOMessage
from spinnman.messages.eieio.eieio_command_header import EIEIOCommandHeader
from spinnman import exceptions

import binascii


class EIEIOCommandMessage(AbstractEIEIOMessage):

    def __init__(self, eieio_command_header, data):
        AbstractEIEIOMessage.__init__(self, data)
        if isinstance(eieio_command_header, EIEIOCommandHeader):
            self._eieio_command_header = eieio_command_header
        else:
            raise exceptions.SpinnmanInvalidParameterException(
                "eieio_command_header", "invaid",
                "the header is not a eieio command header, therefore error has"
                "been raised")
    @property
    def eieio_command_header(self):
        return self._eieio_command_header

    def is_EIEIO_message(self):
        return True

    def __str__(self):
        return "{}:{}".format(self._eieio_command_header,
                              binascii.hexlify(self._data))

    def __repr__(self):
        return self.__str__()