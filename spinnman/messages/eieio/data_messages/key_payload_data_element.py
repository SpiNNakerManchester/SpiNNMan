from spinnman.exceptions import SpinnmanInvalidParameterException
from spinnman.messages.eieio import EIEIOType
from .abstract_data_element import AbstractDataElement

import struct


class KeyPayloadDataElement(AbstractDataElement):
    """ A data element that contains a key and a payload
    """

    def __init__(self, key, payload, payload_is_timestamp=False):
        self._key = key
        self._payload = payload
        self._payload_is_timestamp = payload_is_timestamp

    @property
    def key(self):
        return self._key

    @property
    def payload(self):
        return self._payload

    @property
    def payload_is_timestamp(self):
        return self._payload_is_timestamp

    def get_bytestring(self, eieio_type):
        if eieio_type.payload_bytes == 0:
            raise SpinnmanInvalidParameterException(
                "eieio_type", eieio_type,
                "The type specifies no payload, but this element has a"
                " payload")
        if eieio_type == EIEIOType.KEY_PAYLOAD_16_BIT:
            return struct.pack("<HH", self._key, self._payload)
        elif eieio_type == EIEIOType.KEY_PAYLOAD_32_BIT:
            return struct.pack("<II", self._key, self._payload)
        else:
            raise SpinnmanInvalidParameterException(
                "eieio_type", eieio_type, "Unknown type")

    def __str__(self):
        return "KeyPayloadDataElement:{}:{}".format(
            hex(self._key), hex(self._payload))

    def __repr__(self):
        return self.__str__()
