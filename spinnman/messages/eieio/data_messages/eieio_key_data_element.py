from spinnman.exceptions import SpinnmanInvalidParameterException
from spinnman.messages.eieio.eieio_type import EIEIOType
from spinnman.messages.eieio.data_messages.abstract_eieio_data_element \
    import AbstractEIEIODataElement


class EIEIOKeyDataElement(AbstractEIEIODataElement):
    """ A data element that contains just a key
    """

    def __init__(self, key):
        self._key = key

    @property
    def key(self):
        return self._key

    def write_element(self, eieio_type, byte_writer):
        if eieio_type.payload_bytes != 0:
            raise SpinnmanInvalidParameterException(
                "eieio_type", eieio_type,
                "The type specifies a payload, but this element has no"
                " payload")
        if eieio_type == EIEIOType.KEY_16_BIT:
            byte_writer.write_short(self._key)
        elif eieio_type == EIEIOType.KEY_32_BIT:
            byte_writer.write_int(self._key)
        else:
            raise SpinnmanInvalidParameterException(
                "eieio_type", eieio_type, "Unknown type")

    def __str__(self):
        return "EIEIOKeyDataElement:{}".format(hex(self._key))

    def __repr__(self):
        return self.__str__()
