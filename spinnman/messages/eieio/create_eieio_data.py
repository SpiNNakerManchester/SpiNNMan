
from spinnman.messages.eieio.data_messages.eieio_16bit\
    import EIEIO16BitDataMessage
from spinnman.messages.eieio.data_messages.eieio_16bit\
    import EIEIO16BitLowerKeyPrefixDataMessage
from spinnman.messages.eieio.data_messages.eieio_16bit\
    import EIEIO16BitUpperKeyPrefixDataMessage
from spinnman.messages.eieio.data_messages.eieio_16bit\
    import EIEIO16BitPayloadPrefixDataMessage
from spinnman.messages.eieio.data_messages.eieio_16bit\
    import EIEIO16BitPayloadPrefixLowerKeyPrefixDataMessage
from spinnman.messages.eieio.data_messages.eieio_16bit\
    import EIEIO16BitPayloadPrefixUpperKeyPrefixDataMessage
from spinnman.messages.eieio.data_messages.eieio_16bit\
    import EIEIO16BitTimedPayloadPrefixDataMessage
from spinnman.messages.eieio.data_messages.eieio_16bit\
    import EIEIO16BitTimedPayloadPrefixLowerKeyPrefixDataMessage
from spinnman.messages.eieio.data_messages.eieio_16bit\
    import EIEIO16BitTimedPayloadPrefixUpperKeyPrefixDataMessage
from spinnman.messages.eieio.data_messages.eieio_16bit\
    import EIEIO16BitWithPayloadDataMessage
from spinnman.messages.eieio.data_messages.eieio_16bit\
    import EIEIO16BitWithPayloadLowerKeyPrefixDataMessage
from spinnman.messages.eieio.data_messages.eieio_16bit\
    import EIEIO16BitWithPayloadUpperKeyPrefixDataMessage
from spinnman.messages.eieio.data_messages.eieio_16bit\
    import EIEIO16BitWithPayloadPayloadPrefixDataMessage
from spinnman.messages.eieio.data_messages.eieio_16bit\
    import EIEIO16BitWithPayloadPayloadPrefixLowerKeyPrefixDataMessage
from spinnman.messages.eieio.data_messages.eieio_16bit\
    import EIEIO16BitWithPayloadPayloadPrefixUpperKeyPrefixDataMessage
from spinnman.messages.eieio.data_messages.eieio_16bit\
    import EIEIO16BitWithPayloadTimedDataMessage
from spinnman.messages.eieio.data_messages.eieio_16bit\
    import EIEIO16BitWithPayloadTimedLowerKeyPrefixDataMessage
from spinnman.messages.eieio.data_messages.eieio_16bit\
    import EIEIO16BitWithPayloadTimedUpperKeyPrefixDataMessage
from spinnman.messages.eieio.data_messages.eieio_32bit\
    import EIEIO32BitDataMessage
from spinnman.messages.eieio.data_messages.eieio_32bit\
    import EIEIO32BitLowerKeyPrefixDataMessage
from spinnman.messages.eieio.data_messages.eieio_32bit\
    import EIEIO32BitUpperKeyPrefixDataMessage
from spinnman.messages.eieio.data_messages.eieio_32bit\
    import EIEIO32BitPayloadPrefixDataMessage
from spinnman.messages.eieio.data_messages.eieio_32bit\
    import EIEIO32BitPayloadPrefixLowerKeyPrefixDataMessage
from spinnman.messages.eieio.data_messages.eieio_32bit\
    import EIEIO32BitPayloadPrefixUpperKeyPrefixDataMessage
from spinnman.messages.eieio.data_messages.eieio_32bit\
    import EIEIO32BitTimedPayloadPrefixDataMessage
from spinnman.messages.eieio.data_messages.eieio_32bit\
    import EIEIO32BitTimedPayloadPrefixLowerKeyPrefixDataMessage
from spinnman.messages.eieio.data_messages.eieio_32bit\
    import EIEIO32BitTimedPayloadPrefixUpperKeyPrefixDataMessage
from spinnman.messages.eieio.data_messages.eieio_32bit\
    import EIEIO32BitWithPayloadDataMessage
from spinnman.messages.eieio.data_messages.eieio_32bit\
    import EIEIO32BitWithPayloadLowerKeyPrefixDataMessage
from spinnman.messages.eieio.data_messages.eieio_32bit\
    import EIEIO32BitWithPayloadUpperKeyPrefixDataMessage
from spinnman.messages.eieio.data_messages.eieio_32bit\
    import EIEIO32BitWithPayloadPayloadPrefixDataMessage
from spinnman.messages.eieio.data_messages.eieio_32bit\
    import EIEIO32BitWithPayloadPayloadPrefixLowerKeyPrefixDataMessage
from spinnman.messages.eieio.data_messages.eieio_32bit\
    import EIEIO32BitWithPayloadPayloadPrefixUpperKeyPrefixDataMessage
from spinnman.messages.eieio.data_messages.eieio_32bit\
    import EIEIO32BitWithPayloadTimedDataMessage
from spinnman.messages.eieio.data_messages.eieio_32bit\
    import EIEIO32BitWithPayloadTimedLowerKeyPrefixDataMessage
from spinnman.messages.eieio.data_messages.eieio_32bit\
    import EIEIO32BitWithPayloadTimedUpperKeyPrefixDataMessage
from spinnman.messages.eieio.eieio_prefix import EIEIOPrefix
from spinnman.messages.eieio.data_messages.eieio_data_message\
    import EIEIODataMessage
from spinnman.messages.eieio.data_messages.eieio_data_header\
    import EIEIODataHeader
from spinnman.messages.eieio.eieio_type import EIEIOType
from spinnman.messages.eieio.data_messages.eieio_without_payload_data_message\
    import EIEIOWithoutPayloadDataMessage
from spinnman.messages.eieio.data_messages.eieio_with_payload_data_message\
    import EIEIOWithPayloadDataMessage


def _read_16_bit_message(prefix, payload_base, prefix_type, is_time,
                         data, offset, eieio_header):
    """ Return a packet containing 16 bit elements
    """
    if payload_base is None:
        if prefix is None:
            return EIEIO16BitDataMessage(eieio_header.count, data, offset)
        elif prefix_type == EIEIOPrefix.LOWER_HALF_WORD:
            return EIEIO16BitLowerKeyPrefixDataMessage(
                prefix, eieio_header.count, data, offset)
        elif prefix_type == EIEIOPrefix.UPPER_HALF_WORD:
            return EIEIO16BitUpperKeyPrefixDataMessage(
                prefix, eieio_header.count, data, offset)
    elif payload_base is not None and not is_time:
        if prefix is None:
            return EIEIO16BitPayloadPrefixDataMessage(
                payload_base, eieio_header.count, data, offset)
        elif prefix_type == EIEIOPrefix.LOWER_HALF_WORD:
            return EIEIO16BitPayloadPrefixLowerKeyPrefixDataMessage(
                prefix, payload_base, eieio_header.count, data, offset)
        elif prefix_type == EIEIOPrefix.UPPER_HALF_WORD:
            return EIEIO16BitPayloadPrefixUpperKeyPrefixDataMessage(
                prefix, payload_base, eieio_header.count, data, offset)
    elif payload_base is not None and is_time:
        if prefix is None:
            return EIEIO16BitTimedPayloadPrefixDataMessage(
                payload_base, eieio_header.count, data, offset)
        elif prefix_type == EIEIOPrefix.LOWER_HALF_WORD:
            return EIEIO16BitTimedPayloadPrefixLowerKeyPrefixDataMessage(
                prefix, payload_base, eieio_header.count, data, offset)
        elif prefix_type == EIEIOPrefix.UPPER_HALF_WORD:
            return EIEIO16BitTimedPayloadPrefixUpperKeyPrefixDataMessage(
                prefix, payload_base, eieio_header.count, data, offset)
    return EIEIOWithoutPayloadDataMessage(eieio_header, data, offset)


def _read_16_bit_payload_message(prefix, payload_base, prefix_type,
                                 is_time, data, offset, eieio_header):
    """ Return a packet containing 16 bit elements and payload
    """
    if payload_base is None and not is_time:
        if prefix is None:
            return EIEIO16BitWithPayloadDataMessage(
                eieio_header.count, data, offset)
        elif prefix_type == EIEIOPrefix.LOWER_HALF_WORD:
            return EIEIO16BitWithPayloadLowerKeyPrefixDataMessage(
                prefix, eieio_header.count, data, offset)
        elif prefix_type == EIEIOPrefix.UPPER_HALF_WORD:
            return EIEIO16BitWithPayloadUpperKeyPrefixDataMessage(
                prefix, eieio_header.count, data, offset)
    elif payload_base is not None and not is_time:
        if prefix is None:
            return EIEIO16BitWithPayloadPayloadPrefixDataMessage(
                payload_base, eieio_header.count, data, offset)
        elif prefix_type == EIEIOPrefix.LOWER_HALF_WORD:
            return EIEIO16BitWithPayloadPayloadPrefixLowerKeyPrefixDataMessage(
                prefix, payload_base, eieio_header.count, data, offset)
        elif prefix_type == EIEIOPrefix.UPPER_HALF_WORD:
            return EIEIO16BitWithPayloadPayloadPrefixUpperKeyPrefixDataMessage(
                prefix, payload_base, eieio_header.count, data, offset)
    elif payload_base is None and is_time:
        if prefix is None:
            return EIEIO16BitWithPayloadTimedDataMessage(
                eieio_header.count, data, offset)
        elif prefix_type == EIEIOPrefix.LOWER_HALF_WORD:
            return EIEIO16BitWithPayloadTimedLowerKeyPrefixDataMessage(
                prefix, eieio_header.count, data, offset)
        elif prefix_type == EIEIOPrefix.UPPER_HALF_WORD:
            return EIEIO16BitWithPayloadTimedUpperKeyPrefixDataMessage(
                prefix, eieio_header.count, data, offset)
    return EIEIOWithPayloadDataMessage(eieio_header, data, offset)


def _read_32_bit_message(prefix, payload_base, prefix_type, is_time,
                         data, offset, eieio_header):
    """ Return a packet containing 32 bit elements
    """
    if payload_base is None:
        if prefix is None:
            return EIEIO32BitDataMessage(eieio_header.count, data, offset)
        elif prefix_type == EIEIOPrefix.LOWER_HALF_WORD:
            return EIEIO32BitLowerKeyPrefixDataMessage(
                prefix, eieio_header.count, data, offset)
        elif prefix_type == EIEIOPrefix.UPPER_HALF_WORD:
            return EIEIO32BitUpperKeyPrefixDataMessage(
                prefix, eieio_header.count, data, offset)
    elif payload_base is not None and not is_time:
        if prefix is None:
            return EIEIO32BitPayloadPrefixDataMessage(
                payload_base, eieio_header.count, data, offset)
        elif prefix_type == EIEIOPrefix.LOWER_HALF_WORD:
            return EIEIO32BitPayloadPrefixLowerKeyPrefixDataMessage(
                prefix, payload_base, eieio_header.count, data, offset)
        elif prefix_type == EIEIOPrefix.UPPER_HALF_WORD:
            return EIEIO32BitPayloadPrefixUpperKeyPrefixDataMessage(
                prefix, payload_base, eieio_header.count, data, offset)
    elif payload_base is not None and is_time:
        if prefix is None:
            return EIEIO32BitTimedPayloadPrefixDataMessage(
                payload_base, eieio_header.count, data, offset)
        elif prefix_type == EIEIOPrefix.LOWER_HALF_WORD:
            return EIEIO32BitTimedPayloadPrefixLowerKeyPrefixDataMessage(
                prefix, payload_base, eieio_header.count, data, offset)
        elif prefix_type == EIEIOPrefix.UPPER_HALF_WORD:
            return EIEIO32BitTimedPayloadPrefixUpperKeyPrefixDataMessage(
                prefix, payload_base, eieio_header.count, data, offset)
    return EIEIOWithoutPayloadDataMessage(eieio_header, data, offset)


def _read_32_bit_payload_message(prefix, payload_base, prefix_type,
                                 is_time, data, offset, eieio_header):
    """ Return a packet containing 32 bit elements and payload
    """
    if payload_base is None and not is_time:
        if prefix is None:
            return EIEIO32BitWithPayloadDataMessage(
                eieio_header.count, data, offset)
        elif prefix_type == EIEIOPrefix.LOWER_HALF_WORD:
            return EIEIO32BitWithPayloadLowerKeyPrefixDataMessage(
                prefix, eieio_header.count, data, offset)
        elif prefix_type == EIEIOPrefix.UPPER_HALF_WORD:
            return EIEIO32BitWithPayloadUpperKeyPrefixDataMessage(
                prefix, eieio_header.count, data, offset)
    elif payload_base is not None and not is_time:
        if prefix is None:
            return EIEIO32BitWithPayloadPayloadPrefixDataMessage(
                payload_base, eieio_header.count, data, offset)
        elif prefix_type == EIEIOPrefix.LOWER_HALF_WORD:
            return EIEIO32BitWithPayloadPayloadPrefixLowerKeyPrefixDataMessage(
                prefix, payload_base, eieio_header.count, data, offset)
        elif prefix_type == EIEIOPrefix.UPPER_HALF_WORD:
            return EIEIO32BitWithPayloadPayloadPrefixUpperKeyPrefixDataMessage(
                prefix, payload_base, eieio_header.count, data, offset)
    elif payload_base is None and is_time:
        if prefix is None:
            return EIEIO32BitWithPayloadTimedDataMessage(
                eieio_header.count, data, offset)
        elif prefix_type == EIEIOPrefix.LOWER_HALF_WORD:
            return EIEIO32BitWithPayloadTimedLowerKeyPrefixDataMessage(
                prefix, eieio_header.count, data, offset)
        elif prefix_type == EIEIOPrefix.UPPER_HALF_WORD:
            return EIEIO32BitWithPayloadTimedUpperKeyPrefixDataMessage(
                prefix, eieio_header.count, data, offset)
    return EIEIOWithPayloadDataMessage(eieio_header, data, offset)


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
        return _read_16_bit_message(
            prefix, payload_base, prefix_type, is_time, data, offset,
            eieio_header)
    elif eieio_type == EIEIOType.KEY_PAYLOAD_16_BIT:
        return _read_16_bit_payload_message(
            prefix, payload_base, prefix_type, is_time, data, offset,
            eieio_header)
    elif eieio_type == EIEIOType.KEY_32_BIT:
        return _read_32_bit_message(
            prefix, payload_base, prefix_type, is_time, data, offset,
            eieio_header)
    elif eieio_type == EIEIOType.KEY_PAYLOAD_32_BIT:
        return _read_32_bit_payload_message(
            prefix, payload_base, prefix_type, is_time, data, offset,
            eieio_header)
    return EIEIODataMessage(eieio_header, data, offset)
