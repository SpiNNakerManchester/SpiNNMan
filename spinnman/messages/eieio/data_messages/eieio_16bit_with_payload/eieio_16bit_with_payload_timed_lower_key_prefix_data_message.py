from spinnman.messages.eieio.eieio_type import EIEIOType
from spinnman.messages.eieio.data_messages.eieio_with_payload_data_message\
    import EIEIOWithPayloadDataMessage
from spinnman.messages.eieio.data_messages.eieio_data_message\
    import EIEIODataMessage


class EIEIO16BitWithPayloadTimedLowerKeyPrefixDataMessage(
        EIEIOWithPayloadDataMessage):

    def __init__(self, key_prefix, data_reader=None):

        EIEIOWithPayloadDataMessage.__init__(
            self, EIEIOType.KEY_PAYLOAD_16_BIT, prefix=key_prefix,
            is_time=True, data_reader)

    @staticmethod
    def get_min_packet_length():
        return EIEIODataMessage.min_packet_length(
            EIEIOType.KEY_PAYLOAD_16_BIT, is_prefix=True)
