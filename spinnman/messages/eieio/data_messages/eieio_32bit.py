from spinnman.messages.eieio import EIEIOType, EIEIOPrefix
from spinnman.messages.eieio.data_messages \
    import EIEIOWithoutPayloadDataMessage, EIEIOWithPayloadDataMessage, \
        EIEIODataHeader, EIEIODataMessage


class EIEIO32DataMessage(EIEIOWithoutPayloadDataMessage):
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


class EIEIO32PayloadMessage(EIEIOWithoutPayloadDataMessage):
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


# class EIEIO32BitDataMessage(EIEIO32DataMessage):
#     """ An EIEIO packet containing 32 bit events
#     """
#     def __init__(self, count=0, data=None, offset=0):
#         EIEIO32DataMessage.__init__(
#             self, count=count, data=data, offset=offset)
# 
# 
# class EIEIO32BitLowerKeyPrefixDataMessage(EIEIO32DataMessage):
#     """ An EIEIO packet containing 32 bit events and a key prefix to be\
#         applied to the lower end of the key
#     """
#     def __init__(self, key_prefix, count=0, data=None, offset=0):
#         EIEIO32DataMessage.__init__(
#             self, count=count, data=data, offset=offset,
#             key_prefix=key_prefix)
# 
# 
# class EIEIO32BitPayloadPrefixDataMessage(EIEIO32DataMessage):
#     """ An EIEIO packet containing 32 bit events with a fixed payload
#     """
#     def __init__(self, payload_prefix, count=0, data=None, offset=0):
#         EIEIO32DataMessage.__init__(
#             self, count=count, data=data, offset=offset,
#             payload_prefix=payload_prefix)
# 
# 
# class EIEIO32BitPayloadPrefixLowerKeyPrefixDataMessage(EIEIO32DataMessage):
#     """ An EIEIO packet containing 32 bit events, a key prefix to be applied\
#         to the lower end of the key, and a fixed payload
#     """
#     def __init__(self, key_prefix, payload_prefix, count=0, data=None,
#                  offset=0):
#         EIEIO32DataMessage.__init__(
#             self, count=count, data=data, offset=offset,
#             key_prefix=key_prefix, payload_prefix=payload_prefix)
# 
# 
# class EIEIO32BitPayloadPrefixUpperKeyPrefixDataMessage(EIEIO32DataMessage):
#     """ An EIEIO packet containing 32 bit events, a key prefix to be applied\
#         to the upper end of the key, and a fixed payload
#     """
#     def __init__(self, key_prefix, payload_prefix, count=0, data=None,
#                  offset=0):
#         EIEIO32DataMessage.__init__(
#             self, count=count, data=data, offset=offset,
#             key_prefix=key_prefix, payload_prefix=payload_prefix,
#             prefix_type=EIEIOPrefix.UPPER_HALF_WORD)
# 
# 
# class EIEIO32BitTimedPayloadPrefixDataMessage(EIEIO32DataMessage):
#     """ An EIEIO packet containing 32 bit events with a timestamp for the\
#         events
#     """
#     def __init__(self, timestamp, count=0, data=None, offset=0):
#         EIEIO32DataMessage.__init__(
#             self, count=count, data=data, offset=offset, timestamp=timestamp)
# 
# 
# class EIEIO32BitTimedPayloadPrefixLowerKeyPrefixDataMessage(
#         EIEIO32DataMessage):
#     """ An EIEIO packet containing 32 bit events, a key prefix to be applied\
#         to the lower end of the key, and a timestamp for the events
#     """
#     def __init__(self, key_prefix, timestamp, count=0, data=None, offset=0):
#         EIEIO32DataMessage.__init__(
#             self, count=count, data=data, offset=offset, key_prefix=key_prefix,
#             timestamp=timestamp)
# 
# 
# class EIEIO32BitTimedPayloadPrefixUpperKeyPrefixDataMessage(
#         EIEIO32DataMessage):
#     """ An EIEIO packet containing 32 bit events, a key prefix to be applied\
#         to the upper end of the key, and a timestamp for the events
#     """
#     def __init__(self, key_prefix, timestamp, count=0, data=None, offset=0):
#         EIEIO32DataMessage.__init__(
#             self, count=count, data=data, offset=offset, key_prefix=key_prefix,
#             timestamp=timestamp, prefix_type=EIEIOPrefix.UPPER_HALF_WORD)
# 
# 
# class EIEIO32BitUpperKeyPrefixDataMessage(EIEIO32DataMessage):
#     """ An EIEIO packet containing 32 bit events and a key prefix to be\
#         applied to the upper end of the key
#     """
#     def __init__(self, key_prefix, count=0, data=None, offset=0):
#         EIEIO32DataMessage.__init__(
#             self, count=count, data=data, offset=offset, key_prefix=key_prefix,
#             prefix_type=EIEIOPrefix.UPPER_HALF_WORD)
# 
# class EIEIO32BitWithPayloadDataMessage(EIEIO32PayloadMessage):
#     """ An EIEIO packet containing 32 bit events
#     """
#     def __init__(self, count=0, data=None, offset=0):
#         EIEIO32PayloadMessage.__init__(
#             self, count=count, data=data, offset=offset)
# 
# 
# class EIEIO32BitWithPayloadLowerKeyPrefixDataMessage(EIEIO32PayloadMessage):
#     """ An EIEIO packet containing 32 bit events and a key prefix to be\
#         applied to the lower end of the key
#     """
#     def __init__(self, key_prefix, count=0, data=None, offset=0):
#         EIEIO32PayloadMessage.__init__(
#             self, count=count, data=data, offset=offset,
#             key_prefix=key_prefix)
# 
# 
# class EIEIO32BitWithPayloadPayloadPrefixDataMessage(EIEIO32PayloadMessage):
#     """ An EIEIO packet containing 32 bit events with a fixed payload
#     """
#     def __init__(self, payload_prefix, count=0, data=None, offset=0):
#         EIEIO32PayloadMessage.__init__(
#             self, count=count, data=data, offset=offset,
#             payload_prefix=payload_prefix)
# 
# 
# class EIEIO32BitWithPayloadPayloadPrefixLowerKeyPrefixDataMessage(
#         EIEIO32PayloadMessage):
#     """ An EIEIO packet containing 32 bit events, a key prefix to be applied\
#         to the lower end of the key, and a fixed payload
#     """
#     def __init__(self, key_prefix, payload_prefix, count=0, data=None,
#                  offset=0):
#         EIEIO32PayloadMessage.__init__(
#             self, count=count, data=data, offset=offset,
#             key_prefix=key_prefix, payload_prefix=payload_prefix)
# 
# 
# class EIEIO32BitWithPayloadPayloadPrefixUpperKeyPrefixDataMessage(
#         EIEIO32PayloadMessage):
#     """ An EIEIO packet containing 32 bit events, a key prefix to be applied\
#         to the upper end of the key, and a fixed payload
#     """
#     def __init__(self, key_prefix, payload_prefix, count=0, data=None,
#                  offset=0):
#         EIEIO32PayloadMessage.__init__(
#             self, count=count, data=data, offset=offset,
#             key_prefix=key_prefix, payload_prefix=payload_prefix,
#             prefix_type=EIEIOPrefix.UPPER_HALF_WORD)
# 
# 
# class EIEIO32BitWithPayloadTimedDataMessage(EIEIO32PayloadMessage):
#     """ An EIEIO packet containing 32 bit events with a timestamp for the\
#         events
#     """
#     def __init__(self, timestamp, count=0, data=None, offset=0):
#         EIEIO32PayloadMessage.__init__(
#             self, count=count, data=data, offset=offset, timestamp=timestamp)
# 
# 
# class EIEIO32BitWithPayloadTimedLowerKeyPrefixDataMessage(
#         EIEIO32PayloadMessage):
#     """ An EIEIO packet containing 32 bit events, a key prefix to be applied\
#         to the lower end of the key, and a timestamp for the events
#     """
#     def __init__(self, key_prefix, timestamp, count=0, data=None, offset=0):
#         EIEIO32PayloadMessage.__init__(
#             self, count=count, data=data, offset=offset, key_prefix=key_prefix,
#             timestamp=timestamp)
# 
# 
# class EIEIO32BitWithPayloadTimedUpperKeyPrefixDataMessage(
#         EIEIO32PayloadMessage):
#     """ An EIEIO packet containing 32 bit events, a key prefix to be applied\
#         to the upper end of the key, and a timestamp for the events
#     """
#     def __init__(self, key_prefix, timestamp, count=0, data=None, offset=0):
#         EIEIO32PayloadMessage.__init__(
#             self, count=count, data=data, offset=offset, key_prefix=key_prefix,
#             timestamp=timestamp, prefix_type=EIEIOPrefix.UPPER_HALF_WORD)
# 
# 
# class EIEIO32BitWithPayloadUpperKeyPrefixDataMessage(EIEIO32PayloadMessage):
#     """ An EIEIO packet containing 32 bit events and a key prefix to be\
#         applied to the upper end of the key
#     """
#     def __init__(self, key_prefix, count=0, data=None, offset=0):
#         EIEIO32PayloadMessage.__init__(
#             self, count=count, data=data, offset=offset, key_prefix=key_prefix,
#             prefix_type=EIEIOPrefix.UPPER_HALF_WORD)
