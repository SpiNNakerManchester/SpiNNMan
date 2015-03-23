from spinnman.exceptions import SpinnmanInvalidParameterException
from spinnman.messages.eieio.eieio_type import EIEIOType
from spinnman.messages.eieio.data_messages.abstract_eieio_data_element \
    import AbstractEIEIODataElement


class EIEIOKeyPayloadDataElement(AbstractEIEIODataElement):
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

    def write_element(self, eieio_type, byte_writer):
        if eieio_type.payload_bytes == 0:
            raise SpinnmanInvalidParameterException(
                "eieio_type", eieio_type,
                "The type specifies no payload, but this element has a"
                " payload")
        if eieio_type == EIEIOType.KEY_PAYLOAD_16_BIT:
            byte_writer.write_short(self._key)
            byte_writer.write_short(self._payload)
        elif eieio_type == EIEIOType.KEY_PAYLOAD_32_BIT:
            byte_writer.write_int(self._key)
            byte_writer.write_int(self._payload)
        else:
            raise SpinnmanInvalidParameterException(
                "eieio_type", eieio_type, "Unknown type")

    def __str__(self):
        return "EIEIOKeyPayloadDataElement:{}:{}".format(hex(self._key),
                                                         hex(self._payload))

    def __repr__(self):
        return self.__str__()
