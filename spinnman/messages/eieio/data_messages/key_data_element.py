from spinnman.exceptions import SpinnmanInvalidParameterException
from spinnman.messages.eieio import EIEIOType
from .abstract_data_element import AbstractDataElement

import struct

_ONE_SHORT = struct.Struct("<H")
_ONE_WORD = struct.Struct("<I")


class KeyDataElement(AbstractDataElement):
    """ A data element that contains just a key
    """

    def __init__(self, key):
        self._key = key

    @property
    def key(self):
        return self._key

    def get_bytestring(self, eieio_type):
        if eieio_type.payload_bytes != 0:
            raise SpinnmanInvalidParameterException(
                "eieio_type", eieio_type,
                "The type specifies a payload, but this element has no"
                " payload")
        if eieio_type == EIEIOType.KEY_16_BIT:
            return _ONE_SHORT.pack(self._key)
        elif eieio_type == EIEIOType.KEY_32_BIT:
            return _ONE_WORD.pack(self._key)
        else:
            raise SpinnmanInvalidParameterException(
                "eieio_type", eieio_type, "Unknown type")

    def __str__(self):
        return "KeyDataElement:{}".format(hex(self._key))

    def __repr__(self):
        return self.__str__()
