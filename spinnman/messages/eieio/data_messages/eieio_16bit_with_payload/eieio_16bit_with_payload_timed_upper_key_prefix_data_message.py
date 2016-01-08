from spinnman.messages.eieio.eieio_type import EIEIOType
from spinnman.messages.eieio.eieio_prefix import EIEIOPrefix
from spinnman.messages.eieio.data_messages.eieio_with_payload_data_message\
    import EIEIOWithPayloadDataMessage
from spinnman.messages.eieio.data_messages.eieio_data_header\
    import EIEIODataHeader
from spinnman.messages.eieio.data_messages.eieio_data_message\
    import EIEIODataMessage


class EIEIO16BitWithPayloadTimedUpperKeyPrefixDataMessage(
        EIEIOWithPayloadDataMessage):
    """ An EIEIO packet containing 16 bit events and payloads, where the\
        payloads represent the timestamp of the events, and a key prefix to be\
        applied to the upper end of the key
    """
    def __init__(self, key_prefix, count=0, data=None, offset=0):

        EIEIOWithPayloadDataMessage.__init__(
            self, EIEIODataHeader(EIEIOType.KEY_PAYLOAD_16_BIT,
                                  prefix=key_prefix,
                                  prefix_type=EIEIOPrefix.UPPER_HALF_WORD,
                                  is_time=True, count=count),
            data, offset)

    @staticmethod
    def get_min_packet_length():
        return EIEIODataMessage.min_packet_length(
            EIEIOType.KEY_PAYLOAD_16_BIT, is_prefix=True)
