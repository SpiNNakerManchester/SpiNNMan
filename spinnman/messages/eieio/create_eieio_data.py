from spinnman.messages.eieio.data_messages \
    import EIEIODataMessage, EIEIODataHeader
from spinnman.messages.eieio.data_messages \
    import EIEIOWithoutPayloadDataMessage, EIEIOWithPayloadDataMessage
from spinnman.messages.eieio.data_messages.specialized_message_types\
    import EIEIO16DataMessage, EIEIO16PayloadMessage
from spinnman.messages.eieio.data_messages.specialized_message_types\
    import EIEIO32DataMessage, EIEIO32PayloadMessage
from spinnman.messages.eieio.eieio_type import EIEIOType


def _construct_message(factory, factory2, prefix, payload_base,
                       prefix_type, is_time, data, offset, eieio_header):
    """ Return a packet containing 16 bit elements
    """
    if payload_base is None:
        if prefix is None:
            return factory(eieio_header.count, data, offset)
        return factory(eieio_header.count, data, offset, key_prefix=prefix,
                       prefix_type=prefix_type)
    elif payload_base is not None and not is_time:
        if prefix is None:
            return factory(eieio_header.count, data, offset,
                           payload_prefix=payload_base)
        return factory(eieio_header.count, data, offset,
                       payload_prefix=payload_base,
                       key_prefix=prefix, prefix_type=prefix_type)
    elif payload_base is not None and is_time:
        if prefix is None:
            return factory(eieio_header.count, data, offset,
                           timestamp=payload_base)
        return factory(eieio_header.count, data, offset,
                       timestamp=payload_base,
                       key_prefix=prefix, prefix_type=prefix_type)
    return factory2(eieio_header, data, offset)


def read_eieio_data_message(data, offset):
    """ Reads the content of an EIEIO data message and returns an object\
        identifying the data which was contained in the packet

    :param data: data received from the network as a bytestring
    :type data: str
    :param offset: offset at which the parsing operation should start
    :type offset: int
    :return: an object which inherits from EIEIODataMessage which contains\
            parsed data received from the network
    :rtype:\
            :py:class:`spinnman.messages.eieio.data_messages.eieio_data_message.EIEIODataMessage`
    """
    eieio_header = EIEIODataHeader.from_bytestring(data, offset)
    offset += eieio_header.size
    eieio_type = eieio_header.eieio_type
    prefix = eieio_header.prefix
    payload_base = eieio_header.payload_base
    prefix_type = eieio_header.prefix_type
    is_time = eieio_header.is_time
    if eieio_type == EIEIOType.KEY_16_BIT:
        return _construct_message(
            EIEIO16DataMessage, EIEIOWithoutPayloadDataMessage,
            prefix, payload_base, prefix_type, is_time, data, offset,
            eieio_header)
    elif eieio_type == EIEIOType.KEY_PAYLOAD_16_BIT:
        return _construct_message(
            EIEIO16PayloadMessage, EIEIOWithPayloadDataMessage,
            prefix, payload_base, prefix_type, is_time, data, offset,
            eieio_header)
    elif eieio_type == EIEIOType.KEY_32_BIT:
        return _construct_message(
            EIEIO32DataMessage, EIEIOWithoutPayloadDataMessage,
            prefix, payload_base, prefix_type, is_time, data, offset,
            eieio_header)
    elif eieio_type == EIEIOType.KEY_PAYLOAD_32_BIT:
        return _construct_message(
            EIEIO32PayloadMessage, EIEIOWithPayloadDataMessage,
            prefix, payload_base, prefix_type, is_time, data, offset,
            eieio_header)
    return EIEIODataMessage(eieio_header, data, offset)
