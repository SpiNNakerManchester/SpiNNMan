from spinnman.messages.eieio.abstract_eieio_message import AbstractEIEIOMessage
from spinnman.messages.eieio.eieio_type_param import EIEIOTypeParam
from spinnman import exceptions
import struct

class EIEIOMessage(AbstractEIEIOMessage):

    def __init__(self, eieio_header, data=bytearray()):
        AbstractEIEIOMessage.__init__(self, data)
        self._eieio_header = eieio_header

    @property
    def eieio_header(self):
        return self._eieio_header
    
    def is_EIEIO_message(self):
        return True

    def write_key(self, key):
        if (self._eieio_header.type_param == EIEIOTypeParam.KEY_16_BIT
                or self._eieio_header.type_param == EIEIOTypeParam.KEY_PAYLOAD_16_BIT):
            self._data = struct.pack("<H", key)
        else:
            self._data = struct.pack("<I", key)

    def write_payload(self, payload):
        if self._eieio_header.type_param == EIEIOTypeParam.KEY_PAYLOAD_16_BIT:
            self._data = struct.pack("<H", payload)
        elif self._eieio_header.type_param == EIEIOTypeParam.KEY_PAYLOAD_32_BIT:
            self._data = struct.pack("<I", payload)
        else:
            raise exceptions.SpinnmanInvalidParameterException(
                "Cannot add a payload to a message type that does not support "
                "payloads. Please change the message type and try again", "",
                "")