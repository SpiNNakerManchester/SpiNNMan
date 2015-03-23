from spinnman.messages.eieio.eieio_type import EIEIOType
from spinnman.messages.eieio.data_messages.eieio_with_payload_data_message\
    import EIEIOWithPayloadDataMessage
from spinnman.messages.eieio.data_messages.eieio_data_header\
    import EIEIODataHeader
from spinnman.messages.eieio.data_messages.eieio_data_message\
    import EIEIODataMessage


class EIEIO32BitWithPayloadTimedDataMessage(EIEIOWithPayloadDataMessage):

    def __init__(self, data_reader=None):
        EIEIOWithPayloadDataMessage.__init__(
            self, EIEIODataHeader(EIEIOType.KEY_PAYLOAD_32_BIT, is_time=True),
            data_reader)

    @staticmethod
    def get_min_packet_length():
        return EIEIODataMessage.min_packet_length(EIEIOType.KEY_PAYLOAD_32_BIT)
