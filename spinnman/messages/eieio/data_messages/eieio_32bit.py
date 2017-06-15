from spinnman.messages.eieio import EIEIOType, EIEIOPrefix
from spinnman.messages.eieio.data_messages \
    import EIEIOWithoutPayloadDataMessage, EIEIOWithPayloadDataMessage, \
        EIEIODataHeader, EIEIODataMessage


class _EIEIO32DataMessage(EIEIOWithoutPayloadDataMessage):
    """ An EIEIO packet containing 32 bit events
    """
    def __init__(self, count=0, data=None, offset=0,
                 key_prefix=None, payload_prefix=None, timestamp=None,
                 prefix_type=EIEIOPrefix.LOWER_HALF_WORD):
        payload = payload_prefix
        if timestamp is not None:
            payload = timestamp
        EIEIOWithoutPayloadDataMessage.__init__(
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


class _EIEIO32PayloadMessage(EIEIOWithoutPayloadDataMessage):
    """ An EIEIO packet containing 32 bit events
    """
    def __init__(self, count=0, data=None, offset=0,
                 key_prefix=None, payload_prefix=None, timestamp=None,
                 prefix_type=EIEIOPrefix.LOWER_HALF_WORD):
        payload = payload_prefix
        if timestamp is not None:
            payload = timestamp
        EIEIOWithPayloadDataMessage.__init__(
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


class EIEIO32BitDataMessage(_EIEIO32DataMessage):
    """ An EIEIO packet containing 32 bit events
    """
    def __init__(self, count=0, data=None, offset=0):
        _EIEIO32DataMessage.__init__(
            self, count=count, data=data, offset=offset)


class EIEIO32BitLowerKeyPrefixDataMessage(_EIEIO32DataMessage):
    """ An EIEIO packet containing 32 bit events and a key prefix to be\
        applied to the lower end of the key
    """
    def __init__(self, key_prefix, count=0, data=None, offset=0):
        _EIEIO32DataMessage.__init__(
            self, count=count, data=data, offset=offset,
            key_prefix=key_prefix)


class EIEIO32BitPayloadPrefixDataMessage(_EIEIO32DataMessage):
    """ An EIEIO packet containing 32 bit events with a fixed payload
    """
    def __init__(self, payload_prefix, count=0, data=None, offset=0):
        _EIEIO32DataMessage.__init__(
            self, count=count, data=data, offset=offset,
            payload_prefix=payload_prefix)


class EIEIO32BitPayloadPrefixLowerKeyPrefixDataMessage(_EIEIO32DataMessage):
    """ An EIEIO packet containing 32 bit events, a key prefix to be applied\
        to the lower end of the key, and a fixed payload
    """
    def __init__(self, key_prefix, payload_prefix, count=0, data=None,
                 offset=0):
        _EIEIO32DataMessage.__init__(
            self, count=count, data=data, offset=offset,
            key_prefix=key_prefix, payload_prefix=payload_prefix)


class EIEIO32BitPayloadPrefixUpperKeyPrefixDataMessage(_EIEIO32DataMessage):
    """ An EIEIO packet containing 32 bit events, a key prefix to be applied\
        to the upper end of the key, and a fixed payload
    """
    def __init__(self, key_prefix, payload_prefix, count=0, data=None,
                 offset=0):
        _EIEIO32DataMessage.__init__(
            self, count=count, data=data, offset=offset,
            key_prefix=key_prefix, payload_prefix=payload_prefix,
            prefix_type=EIEIOPrefix.UPPER_HALF_WORD)


class EIEIO32BitTimedPayloadPrefixDataMessage(_EIEIO32DataMessage):
    """ An EIEIO packet containing 32 bit events with a timestamp for the\
        events
    """
    def __init__(self, timestamp, count=0, data=None, offset=0):
        _EIEIO32DataMessage.__init__(
            self, count=count, data=data, offset=offset, timestamp=timestamp)


class EIEIO32BitTimedPayloadPrefixLowerKeyPrefixDataMessage(
        _EIEIO32DataMessage):
    """ An EIEIO packet containing 32 bit events, a key prefix to be applied\
        to the lower end of the key, and a timestamp for the events
    """
    def __init__(self, key_prefix, timestamp, count=0, data=None, offset=0):
        _EIEIO32DataMessage.__init__(
            self, count=count, data=data, offset=offset, key_prefix=key_prefix,
            timestamp=timestamp)


class EIEIO32BitTimedPayloadPrefixUpperKeyPrefixDataMessage(
        _EIEIO32DataMessage):
    """ An EIEIO packet containing 32 bit events, a key prefix to be applied\
        to the upper end of the key, and a timestamp for the events
    """
    def __init__(self, key_prefix, timestamp, count=0, data=None, offset=0):
        _EIEIO32DataMessage.__init__(
            self, count=count, data=data, offset=offset, key_prefix=key_prefix,
            timestamp=timestamp, prefix_type=EIEIOPrefix.UPPER_HALF_WORD)


class EIEIO32BitUpperKeyPrefixDataMessage(_EIEIO32DataMessage):
    """ An EIEIO packet containing 32 bit events and a key prefix to be\
        applied to the upper end of the key
    """
    def __init__(self, key_prefix, count=0, data=None, offset=0):
        _EIEIO32DataMessage.__init__(
            self, count=count, data=data, offset=offset, key_prefix=key_prefix,
            prefix_type=EIEIOPrefix.UPPER_HALF_WORD)

class EIEIO32BitWithPayloadDataMessage(_EIEIO32PayloadMessage):
    """ An EIEIO packet containing 32 bit events
    """
    def __init__(self, count=0, data=None, offset=0):
        _EIEIO32PayloadMessage.__init__(
            self, count=count, data=data, offset=offset)


class EIEIO32BitWithPayloadLowerKeyPrefixDataMessage(_EIEIO32PayloadMessage):
    """ An EIEIO packet containing 32 bit events and a key prefix to be\
        applied to the lower end of the key
    """
    def __init__(self, key_prefix, count=0, data=None, offset=0):
        _EIEIO32PayloadMessage.__init__(
            self, count=count, data=data, offset=offset,
            key_prefix=key_prefix)


class EIEIO32BitWithPayloadPayloadPrefixDataMessage(_EIEIO32PayloadMessage):
    """ An EIEIO packet containing 32 bit events with a fixed payload
    """
    def __init__(self, payload_prefix, count=0, data=None, offset=0):
        _EIEIO32PayloadMessage.__init__(
            self, count=count, data=data, offset=offset,
            payload_prefix=payload_prefix)


class EIEIO32BitWithPayloadPayloadPrefixLowerKeyPrefixDataMessage(
        _EIEIO32PayloadMessage):
    """ An EIEIO packet containing 32 bit events, a key prefix to be applied\
        to the lower end of the key, and a fixed payload
    """
    def __init__(self, key_prefix, payload_prefix, count=0, data=None,
                 offset=0):
        _EIEIO32PayloadMessage.__init__(
            self, count=count, data=data, offset=offset,
            key_prefix=key_prefix, payload_prefix=payload_prefix)


class EIEIO32BitWithPayloadPayloadPrefixUpperKeyPrefixDataMessage(
        _EIEIO32PayloadMessage):
    """ An EIEIO packet containing 32 bit events, a key prefix to be applied\
        to the upper end of the key, and a fixed payload
    """
    def __init__(self, key_prefix, payload_prefix, count=0, data=None,
                 offset=0):
        _EIEIO32PayloadMessage.__init__(
            self, count=count, data=data, offset=offset,
            key_prefix=key_prefix, payload_prefix=payload_prefix,
            prefix_type=EIEIOPrefix.UPPER_HALF_WORD)


class EIEIO32BitWithPayloadTimedDataMessage(_EIEIO32PayloadMessage):
    """ An EIEIO packet containing 32 bit events with a timestamp for the\
        events
    """
    def __init__(self, timestamp, count=0, data=None, offset=0):
        _EIEIO32PayloadMessage.__init__(
            self, count=count, data=data, offset=offset, timestamp=timestamp)


class EIEIO32BitWithPayloadTimedLowerKeyPrefixDataMessage(
        _EIEIO32PayloadMessage):
    """ An EIEIO packet containing 32 bit events, a key prefix to be applied\
        to the lower end of the key, and a timestamp for the events
    """
    def __init__(self, key_prefix, timestamp, count=0, data=None, offset=0):
        _EIEIO32PayloadMessage.__init__(
            self, count=count, data=data, offset=offset, key_prefix=key_prefix,
            timestamp=timestamp)


class EIEIO32BitWithPayloadTimedUpperKeyPrefixDataMessage(
        _EIEIO32PayloadMessage):
    """ An EIEIO packet containing 32 bit events, a key prefix to be applied\
        to the upper end of the key, and a timestamp for the events
    """
    def __init__(self, key_prefix, timestamp, count=0, data=None, offset=0):
        _EIEIO32PayloadMessage.__init__(
            self, count=count, data=data, offset=offset, key_prefix=key_prefix,
            timestamp=timestamp, prefix_type=EIEIOPrefix.UPPER_HALF_WORD)


class EIEIO32BitWithPayloadUpperKeyPrefixDataMessage(_EIEIO32PayloadMessage):
    """ An EIEIO packet containing 32 bit events and a key prefix to be\
        applied to the upper end of the key
    """
    def __init__(self, key_prefix, count=0, data=None, offset=0):
        _EIEIO32PayloadMessage.__init__(
            self, count=count, data=data, offset=offset, key_prefix=key_prefix,
            prefix_type=EIEIOPrefix.UPPER_HALF_WORD)
