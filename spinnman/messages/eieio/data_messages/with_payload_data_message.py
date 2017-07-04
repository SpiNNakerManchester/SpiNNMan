from spinnman.exceptions import SpinnmanInvalidParameterException
from .eieio_data_message import EIEIODataMessage
from .key_payload_data_element import KeyPayloadDataElement


class WithPayloadDataMessage(EIEIODataMessage):
    """ An EIEIO message with a payload
    """

    def __init__(self, eieio_header, data=None, offset=0):
        EIEIODataMessage.__init__(self, eieio_header, data, offset)

        if eieio_header.eieio_type.payload_bytes == 0:
            raise SpinnmanInvalidParameterException(
                "eieio_header", eieio_header,
                "This message should have a payload, but the header indicates"
                " that it doesn't")

    def add_key_and_payload(self, key, payload):
        """ Adds a key and payload to the packet

        :param key: The key to add
        :type key: int
        :param payload: The payload to add
        :type payload: int
        :raise SpinnmanInvalidParameterException: If the key or payload is too\
                    big for the format
        """
        if key > self._header.eieio_type.max_value:
            raise SpinnmanInvalidParameterException(
                "key", key,
                "Larger than the maximum allowed of {}".format(
                    self._header.eieio_type.max_value))
        if payload > self._header.eieio_type.max_value:
            raise SpinnmanInvalidParameterException(
                "payload", payload,
                "Larger than the maximum allowed of {}".format(
                    self._header.eieio_type.max_value))

        EIEIODataMessage.add_element(
            self, KeyPayloadDataElement(
                key, payload, self._header.is_time))
