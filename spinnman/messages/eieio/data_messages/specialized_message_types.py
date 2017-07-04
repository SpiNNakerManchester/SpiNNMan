from spinnman.messages.eieio import EIEIOType, EIEIOPrefix
from .eieio_data_header import EIEIODataHeader
from .eieio_data_message import EIEIODataMessage
from .without_payload_data_message import WithoutPayloadDataMessage
from .with_payload_data_message import WithPayloadDataMessage


class EIEIO16DataMessage(WithoutPayloadDataMessage):
    """ An EIEIO packet containing 16 bit events
    """
    def __init__(self, count=0, data=None, offset=0,
                 key_prefix=None, payload_prefix=None, timestamp=None,
                 prefix_type=EIEIOPrefix.LOWER_HALF_WORD):
        payload = payload_prefix
        if timestamp is not None:
            payload = timestamp
        WithoutPayloadDataMessage.__init__(
            self, EIEIODataHeader(
                EIEIOType.KEY_16_BIT, count=count, prefix=key_prefix,
                payload_base=payload, prefix_type=prefix_type,
                is_time=timestamp is not None),
            data, offset)
        self._prefix = key_prefix is not None
        self._payload = payload is not None

    def get_min_packet_length(self):
        return EIEIODataMessage.min_packet_length(
            EIEIOType.KEY_16_BIT, is_prefix=self._prefix,
            is_payload_base=self._payload)


class EIEIO16PayloadMessage(WithPayloadDataMessage):
    """ An EIEIO packet containing 16 bit events
    """
    def __init__(self, count=0, data=None, offset=0,
                 key_prefix=None, payload_prefix=None, timestamp=None,
                 prefix_type=EIEIOPrefix.LOWER_HALF_WORD):
        payload = payload_prefix
        if timestamp is not None:
            payload = timestamp
        WithPayloadDataMessage.__init__(
            self, EIEIODataHeader(
                EIEIOType.KEY_PAYLOAD_16_BIT, count=count, prefix=key_prefix,
                payload_base=payload, prefix_type=prefix_type,
                is_time=timestamp is not None),
            data, offset)
        self._prefix = key_prefix is not None
        self._payload = payload is not None

    def get_min_packet_length(self):
        return EIEIODataMessage.min_packet_length(
            EIEIOType.KEY_PAYLOAD_16_BIT, is_prefix=self._prefix,
            is_payload_base=self._payload)


class EIEIO32DataMessage(WithoutPayloadDataMessage):
    """ An EIEIO packet containing 32 bit events
    """
    def __init__(self, count=0, data=None, offset=0,
                 key_prefix=None, payload_prefix=None, timestamp=None,
                 prefix_type=EIEIOPrefix.LOWER_HALF_WORD):
        payload = payload_prefix
        if timestamp is not None:
            payload = timestamp
        WithoutPayloadDataMessage.__init__(
            self, EIEIODataHeader(
                EIEIOType.KEY_32_BIT, count=count, prefix=key_prefix,
                payload_base=payload, prefix_type=prefix_type,
                is_time=timestamp is not None),
            data, offset)
        self._prefix = key_prefix is not None
        self._payload = payload is not None

    def get_min_packet_length(self):
        return EIEIODataMessage.min_packet_length(
            EIEIOType.KEY_32_BIT, is_prefix=self._prefix,
            is_payload_base=self._payload)


class EIEIO32PayloadMessage(WithoutPayloadDataMessage):
    """ An EIEIO packet containing 32 bit events
    """
    def __init__(self, count=0, data=None, offset=0,
                 key_prefix=None, payload_prefix=None, timestamp=None,
                 prefix_type=EIEIOPrefix.LOWER_HALF_WORD):
        payload = payload_prefix
        if timestamp is not None:
            payload = timestamp
        WithPayloadDataMessage.__init__(
            self, EIEIODataHeader(
                EIEIOType.KEY_PAYLOAD_32_BIT, count=count, prefix=key_prefix,
                payload_base=payload, prefix_type=prefix_type,
                is_time=timestamp is not None),
            data, offset)
        self._prefix = key_prefix is not None
        self._payload = payload is not None

    def get_min_packet_length(self):
        return EIEIODataMessage.min_packet_length(
            EIEIOType.KEY_PAYLOAD_32_BIT, is_prefix=self._prefix,
            is_payload_base=self._payload)


class EIEIO32BitTimedPayloadPrefixDataMessage(EIEIO32DataMessage):
    """ An EIEIO packet containing 32 bit events with a timestamp for the\
        events
    """
    def __init__(self, timestamp, count=0, data=None, offset=0):
        EIEIO32DataMessage.__init__(
            self, count=count, data=data, offset=offset, timestamp=timestamp)
