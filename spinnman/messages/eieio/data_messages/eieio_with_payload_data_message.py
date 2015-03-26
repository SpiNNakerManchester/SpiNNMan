from spinnman.messages.eieio.data_messages.eieio_data_message\
    import EIEIODataMessage
from spinnman.exceptions import SpinnmanInvalidParameterException
from spinnman.messages.eieio.data_messages.eieio_key_payload_data_element \
    import EIEIOKeyPayloadDataElement


class EIEIOWithPayloadDataMessage(EIEIODataMessage):
    """ An EIEIO message with a payload
    """

    def __init__(self, eieio_header, data_reader=None):
        EIEIODataMessage.__init__(self, eieio_header, data_reader=data_reader)

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
        if key > self._eieio_header.eieio_type.max_value:
            raise SpinnmanInvalidParameterException(
                "key", key,
                "Larger than the maximum allowed of {}".format(
                    self._eieio_header.eieio_type.max_value))
        if payload > self._eieio_header.eieio_type.max_value:
            raise SpinnmanInvalidParameterException(
                "payload", payload,
                "Larger than the maximum allowed of {}".format(
                    self._eieio_header.eieio_type.max_value))
        EIEIODataMessage.add_element(
            self, EIEIOKeyPayloadDataElement(key, payload,
                                             self._eieio_header.is_time))
