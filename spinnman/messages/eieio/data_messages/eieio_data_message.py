from spinnman.exceptions import SpinnmanInvalidParameterException
from spinnman.exceptions import SpinnmanInvalidPacketException
from spinnman.messages.eieio.data_messages.eieio_key_payload_data_element\
    import EIEIOKeyPayloadDataElement
from spinnman.messages.eieio.data_messages.eieio_key_data_element\
    import EIEIOKeyDataElement
from spinnman.messages.eieio.data_messages.eieio_data_header\
    import EIEIODataHeader
from spinnman.messages.eieio.abstract_messages.abstract_eieio_message\
    import AbstractEIEIOMessage
from spinnman.messages.eieio.eieio_type import EIEIOType
from spinnman.messages.eieio.eieio_prefix import EIEIOPrefix
from spinnman import constants

from spinnman.messages.eieio.data_messages.eieio_16bit\
    .eieio_16bit_data_message import EIEIO16BitDataMessage
from spinnman.messages.eieio.data_messages.eieio_16bit\
    .eieio_16bit_lower_key_prefix_data_message\
    import EIEIO16BitLowerKeyPrefixDataMessage
from spinnman.messages.eieio.data_messages.eieio_16bit\
    .eieio_16bit_upper_key_prefix_data_message\
    import EIEIO16BitUpperKeyPrefixDataMessage
from spinnman.messages.eieio.data_messages.eieio_16bit\
    .eieio_16bit_payload_prefix_data_message\
    import EIEIO16BitPayloadPrefixDataMessage
from spinnman.messages.eieio.data_messages.eieio_16bit\
    .eieio_16bit_payload_prefix_lower_key_prefix_data_message\
    import EIEIO16BitPayloadPrefixLowerKeyPrefixDataMessage
from spinnman.messages.eieio.data_messages.eieio_16bit\
    .eieio_16bit_payload_prefix_upper_key_prefix_data_message\
    import EIEIO16BitPayloadPrefixUpperKeyPrefixDataMessage
from spinnman.messages.eieio.data_messages.eieio_16bit\
    .eieio_16bit_timed_payload_prefix_data_message\
    import EIEIO16BitTimedPayloadPrefixDataMessage
from spinnman.messages.eieio.data_messages.eieio_16bit\
    .eieio_16bit_timed_payload_prefix_lower_key_prefix_data_message\
    import EIEIO16BitTimedPayloadPrefixLowerKeyPrefixDataMessage
from spinnman.messages.eieio.data_messages.eieio_16bit\
    .eieio_16bit_timed_payload_prefix_upper_key_prefix_data_message\
    import EIEIO16BitTimedPayloadPrefixUpperKeyPrefixDataMessage
from spinnman.messages.eieio.data_messages.eieio_16bit_with_payload\
    .eieio_16bit_with_payload_data_message\
    import EIEIO16BitWithPayloadDataMessage
from spinnman.messages.eieio.data_messages.eieio_16bit_with_payload\
    .eieio_16bit_with_payload_lower_key_prefix_data_message\
    import EIEIO16BitWithPayloadLowerKeyPrefixDataMessage
from spinnman.messages.eieio.data_messages.eieio_16bit_with_payload\
    .eieio_16bit_with_payload_upper_key_prefix_data_message\
    import EIEIO16BitWithPayloadUpperKeyPrefixDataMessage
from spinnman.messages.eieio.data_messages.eieio_16bit_with_payload\
    .eieio_16bit_with_payload_payload_prefix_data_message\
    import EIEIO16BitWithPayloadPayloadPrefixDataMessage
from spinnman.messages.eieio.data_messages.eieio_16bit_with_payload\
    .eieio_16bit_with_payload_payload_prefix_lower_key_prefix_data_message\
    import EIEIO16BitWithPayloadPayloadPrefixLowerKeyPrefixDataMessage
from spinnman.messages.eieio.data_messages.eieio_16bit_with_payload\
    .eieio_16bit_with_payload_payload_prefix_upper_key_prefix_data_message\
    import EIEIO16BitWithPayloadPayloadPrefixUpperKeyPrefixDataMessage
from spinnman.messages.eieio.data_messages.eieio_16bit_with_payload\
    .eieio_16bit_with_payload_timed_data_message\
    import EIEIO16BitWithPayloadTimedDataMessage
from spinnman.messages.eieio.data_messages.eieio_16bit_with_payload\
    .eieio_16bit_with_payload_timed_lower_key_prefix_data_message\
    import EIEIO16BitWithPayloadTimedLowerKeyPrefixDataMessage
from spinnman.messages.eieio.data_messages.eieio_16bit_with_payload\
    .eieio_16bit_with_payload_timed_upper_key_prefix_data_message\
    import EIEIO16BitWithPayloadTimedUpperKeyPrefixDataMessage
from spinnman.messages.eieio.data_messages.eieio_32bit\
    .eieio_32bit_data_message import EIEIO32BitDataMessage
from spinnman.messages.eieio.data_messages.eieio_32bit\
    .eieio_32bit_lower_key_prefix_data_message\
    import EIEIO32BitLowerKeyPrefixDataMessage
from spinnman.messages.eieio.data_messages.eieio_32bit\
    .eieio_32bit_upper_key_prefix_data_message\
    import EIEIO32BitUpperKeyPrefixDataMessage
from spinnman.messages.eieio.data_messages.eieio_32bit\
    .eieio_32bit_payload_prefix_data_message\
    import EIEIO32BitPayloadPrefixDataMessage
from spinnman.messages.eieio.data_messages.eieio_32bit\
    .eieio_32bit_payload_prefix_lower_key_prefix_data_message\
    import EIEIO32BitPayloadPrefixLowerKeyPrefixDataMessage
from spinnman.messages.eieio.data_messages.eieio_32bit\
    .eieio_32bit_payload_prefix_upper_key_prefix_data_message\
    import EIEIO32BitPayloadPrefixUpperKeyPrefixDataMessage
from spinnman.messages.eieio.data_messages.eieio_32bit\
    .eieio_32bit_timed_payload_prefix_data_message\
    import EIEIO32BitTimedPayloadPrefixDataMessage
from spinnman.messages.eieio.data_messages.eieio_32bit\
    .eieio_32bit_timed_payload_prefix_lower_key_prefix_data_message\
    import EIEIO32BitTimedPayloadPrefixLowerKeyPrefixDataMessage
from spinnman.messages.eieio.data_messages.eieio_32bit\
    .eieio_32bit_timed_payload_prefix_upper_key_prefix_data_message\
    import EIEIO32BitTimedPayloadPrefixUpperKeyPrefixDataMessage
from spinnman.messages.eieio.data_messages.eieio_32bit_with_payload\
    .eieio_32bit_with_payload_data_message\
    import EIEIO32BitWithPayloadDataMessage
from spinnman.messages.eieio.data_messages.eieio_32bit_with_payload\
    .eieio_32bit_with_payload_lower_key_prefix_data_message\
    import EIEIO32BitWithPayloadLowerKeyPrefixDataMessage
from spinnman.messages.eieio.data_messages.eieio_32bit_with_payload\
    .eieio_32bit_with_payload_upper_key_prefix_data_message\
    import EIEIO32BitWithPayloadUpperKeyPrefixDataMessage
from spinnman.messages.eieio.data_messages.eieio_32bit_with_payload\
    .eieio_32bit_with_payload_payload_prefix_data_message\
    import EIEIO32BitWithPayloadPayloadPrefixDataMessage
from spinnman.messages.eieio.data_messages.eieio_32bit_with_payload\
    .eieio_32bit_with_payload_payload_prefix_lower_key_prefix_data_message\
    import EIEIO32BitWithPayloadPayloadPrefixLowerKeyPrefixDataMessage
from spinnman.messages.eieio.data_messages.eieio_32bit_with_payload\
    .eieio_32bit_with_payload_payload_prefix_upper_key_prefix_data_message\
    import EIEIO32BitWithPayloadPayloadPrefixUpperKeyPrefixDataMessage
from spinnman.messages.eieio.data_messages.eieio_32bit_with_payload\
    .eieio_32bit_with_payload_timed_data_message\
    import EIEIO32BitWithPayloadTimedDataMessage
from spinnman.messages.eieio.data_messages.eieio_32bit_with_payload\
    .eieio_32bit_with_payload_timed_lower_key_prefix_data_message\
    import EIEIO32BitWithPayloadTimedLowerKeyPrefixDataMessage
from spinnman.messages.eieio.data_messages.eieio_32bit_with_payload\
    .eieio_32bit_with_payload_timed_upper_key_prefix_data_message\
    import EIEIO32BitWithPayloadTimedUpperKeyPrefixDataMessage

import math


class EIEIODataMessage(AbstractEIEIOMessage):
    """ An EIEIO Data message
    """

    def __init__(self, eieio_header, data_reader=None):
        """

        :param eieio_header: The header of the message
        :type eieio_header:\
                    :py:class:`spinnman.messages.eieio.data_messages.eieio_data_header.EIEIODataHeader`
        :param data_reader: Optional reader of data contained within the\
                            packet, or None if this packet is being written
        :type data_reader:\
                    :py:class:`spinnman.data.abstract_data_reader.AbstractDataReader`
        """

        # The header
        self._eieio_header = eieio_header

        # Elements to be written
        self._elements = list()

        # Keeping track of the reading of the data
        self._data_reader = data_reader
        self._elements_read = 0

    @property
    def eieio_header(self):
        return self._eieio_header

    @staticmethod
    def min_packet_length(eieio_type, is_prefix=False, is_payload_base=False):
        """ The minimum length of a message with the given header, in bytes

        :param eieio_type: the type of message
        :type eieio_type:\
                    :py:class:`spinnman.spinnman.messages.eieio.eieio_type.EIEIOType`
        :param is_prefix: True if there is a prefix, False otherwise
        :type is_prefix: bool
        :param is_payload_base: True if there is a payload base, False\
                    otherwise
        :type is_payload_base: bool
        :return: The minimum size of the packet in bytes
        :rtype: int
        """
        header_size = EIEIODataHeader.get_header_size(eieio_type, is_prefix,
                                                      is_payload_base)
        return header_size + eieio_type.payload_bytes

    @property
    def max_n_elements(self):
        """ The maximum number of elements that can fit in the packet

        :rtype: int
        """
        return int(math.floor((constants.UDP_MESSAGE_MAX_SIZE -
                               self._eieio_header.size) /
                              (self._eieio_header.eieio_type.key_bytes +
                               self._eieio_header.eieio_type.payload_bytes)))

    @property
    def n_elements(self):
        """ The number of elements in the packet
        """
        return self._eieio_header.count

    @property
    def size(self):
        """ The size of the packet with the current contents
        """
        return (self._eieio_header.size +
                ((self._eieio_header.eieio_type.key_bytes +
                 self._eieio_header.eieio_type.payload_bytes) *
                 self._eieio_header.count))

    def add_element(self, element):
        """ Add an element to the message.  The correct type of element must\
            be added, depending on the header values

        :param element: The element to be added
        :type element:\
                    :py:class:`spinnman.messages.eieio.data_messages.abstract_eieio_data_element.AbstractEIEIODataElement`
        :raise SpinnmanInvalidParameterException: If the element is not\
                    compatible with the header
        :raise SpinnmanInvalidPacketException: If the message was created to\
                    read data from a reader
        """
        if self._data_reader is not None:
            raise SpinnmanInvalidPacketException(
                "EIEIODataMessage", "This packet is read-only")

        if (self._eieio_header.eieio_type.payload_bytes == 0 and
                isinstance(element, EIEIOKeyPayloadDataElement)):
            raise SpinnmanInvalidParameterException(
                "element", element,
                "The element has a payload, but the header says no payload")
        if (self._eieio_header.eieio_type.payload_bytes != 0 and
                isinstance(element, EIEIOKeyDataElement)):
            raise SpinnmanInvalidParameterException(
                "element", element,
                "The element has nopayload, but the header says payload")

        self._elements.append(element)
        self._eieio_header.increment_count()

    @property
    def is_next_element(self):
        """ Determine if there is another element to be read

        :return: True if the message was created with data, and there are more\
                    elements to be read
        :rtype: bool
        """
        return (self._data_reader is not None and
                self._elements_read < self._eieio_header.count)

    @property
    def next_element(self):
        """ The next element to be read, or None if no more elements.  The\
            exact type of element returned depends on the packet type

        :rtype:\
                    :py:class:`spinnman.messages.eieio.data_messages.abstract_eieio_data_element.AbstractEIEIODataElement`
        """
        if not self.is_next_element():
            return None
        key = None
        payload = None
        if self._eieio_header.eieio_type == EIEIOType.KEY_16_BIT:
            key = self._data_reader.read_short()
        if self._eieio_header.eieio_type == EIEIOType.KEY_32_BIT:
            key = self._data_reader.read_int()
        if self._eieio_header.eieio_type == EIEIOType.KEY_PAYLOAD_16_BIT:
            key = self._data_reader.read_short()
            payload = self._data_reader.read_short()
        if self._eieio_header.eieio_type == EIEIOType.KEY_PAYLOAD_32_BIT:
            key = self._data_reader.read_int()
            payload = self._data_reader.read_int()

        if self._eieio_header.prefix is not None:
            if self._eieio_header.prefix_type == EIEIOPrefix.UPPER_HALF_WORD:
                key = key | (self._eieio_header.prefix << 16)
            else:
                key = key | self._eieio_header.prefix

        if self._eieio_header.payload_base is not None:
            if payload is not None:
                payload = payload | self._eieio_header.payload_base
            else:
                payload = self._eieio_header.payload_base

        if payload is None:
            return EIEIOKeyDataElement(key)
        else:
            return EIEIOKeyPayloadDataElement(key, payload,
                                              self._eieio_header.is_time)

    def write_eieio_message(self, byte_writer):
        self._eieio_header.write_eieio_header(byte_writer)
        for element in self._elements:
            element.write_element(self._eieio_header.eieio_type, byte_writer)

    @staticmethod
    def _read_16_bit_message(prefix, payload_base, prefix_type, is_time,
                             byte_reader, eieio_header):
        if payload_base is None:
            if prefix is None:
                return EIEIO16BitDataMessage(byte_reader)
            elif prefix_type == EIEIOPrefix.LOWER_HALF_WORD:
                return EIEIO16BitLowerKeyPrefixDataMessage(
                    prefix, byte_reader)
            elif prefix_type == EIEIOPrefix.UPPER_HALF_WORD:
                return EIEIO16BitUpperKeyPrefixDataMessage(
                    prefix, byte_reader)
        elif payload_base is not None and not is_time:
            if prefix is None:
                return EIEIO16BitPayloadPrefixDataMessage(
                    payload_base, byte_reader)
            elif prefix_type == EIEIOPrefix.LOWER_HALF_WORD:
                return EIEIO16BitPayloadPrefixLowerKeyPrefixDataMessage(
                    prefix, payload_base, byte_reader)
            elif prefix_type == EIEIOPrefix.UPPER_HALF_WORD:
                return EIEIO16BitPayloadPrefixUpperKeyPrefixDataMessage(
                    prefix, payload_base, byte_reader)
        elif payload_base is not None and is_time:
            if prefix is None:
                return EIEIO16BitTimedPayloadPrefixDataMessage(
                    payload_base, byte_reader)
            elif prefix_type == EIEIOPrefix.LOWER_HALF_WORD:
                return EIEIO16BitTimedPayloadPrefixLowerKeyPrefixDataMessage(
                    prefix, payload_base, byte_reader)
            elif prefix_type == EIEIOPrefix.UPPER_HALF_WORD:
                return EIEIO16BitTimedPayloadPrefixUpperKeyPrefixDataMessage(
                    prefix, payload_base, byte_reader)
        return EIEIODataMessage(eieio_header, byte_reader)

    @staticmethod
    def _read_16_bit_payload_message(prefix, payload_base, prefix_type,
                                     is_time, byte_reader, eieio_header):
        if payload_base is None and not is_time:
            if prefix is None:
                return EIEIO16BitWithPayloadDataMessage(byte_reader)
            elif prefix_type == EIEIOPrefix.LOWER_HALF_WORD:
                return EIEIO16BitWithPayloadLowerKeyPrefixDataMessage(
                    prefix, byte_reader)
            elif prefix_type == EIEIOPrefix.UPPER_HALF_WORD:
                return EIEIO16BitWithPayloadUpperKeyPrefixDataMessage(
                    prefix, byte_reader)
        elif payload_base is not None and not is_time:
            if prefix is None:
                return EIEIO16BitWithPayloadPayloadPrefixDataMessage(
                    payload_base, byte_reader)
            elif prefix_type == EIEIOPrefix.LOWER_HALF_WORD:
                return EIEIO16BitWithPayloadPayloadPrefixLowerKeyPrefixDataMessage(
                    prefix, payload_base, byte_reader)
            elif prefix_type == EIEIOPrefix.UPPER_HALF_WORD:
                return EIEIO16BitWithPayloadPayloadPrefixUpperKeyPrefixDataMessage(
                    prefix, payload_base, byte_reader)
        elif payload_base is None and is_time:
            if prefix is None:
                return EIEIO16BitWithPayloadTimedDataMessage(byte_reader)
            elif prefix_type == EIEIOPrefix.LOWER_HALF_WORD:
                return EIEIO16BitWithPayloadTimedLowerKeyPrefixDataMessage(
                    prefix, byte_reader)
            elif prefix_type == EIEIOPrefix.UPPER_HALF_WORD:
                return EIEIO16BitWithPayloadTimedUpperKeyPrefixDataMessage(
                    prefix, byte_reader)
        return EIEIODataMessage(eieio_header, byte_reader)

    @staticmethod
    def _read_32_bit_message(prefix, payload_base, prefix_type, is_time,
                             byte_reader, eieio_header):
        if payload_base is None:
            if prefix is None:
                return EIEIO32BitDataMessage(byte_reader)
            elif prefix_type == EIEIOPrefix.LOWER_HALF_WORD:
                return EIEIO32BitLowerKeyPrefixDataMessage(
                    prefix, byte_reader)
            elif prefix_type == EIEIOPrefix.UPPER_HALF_WORD:
                return EIEIO32BitUpperKeyPrefixDataMessage(
                    prefix, byte_reader)
        elif payload_base is not None and not is_time:
            if prefix is None:
                return EIEIO32BitPayloadPrefixDataMessage(
                    payload_base, byte_reader)
            elif prefix_type == EIEIOPrefix.LOWER_HALF_WORD:
                return EIEIO32BitPayloadPrefixLowerKeyPrefixDataMessage(
                    prefix, payload_base, byte_reader)
            elif prefix_type == EIEIOPrefix.UPPER_HALF_WORD:
                return EIEIO32BitPayloadPrefixUpperKeyPrefixDataMessage(
                    prefix, payload_base, byte_reader)
        elif payload_base is not None and is_time:
            if prefix is None:
                return EIEIO32BitTimedPayloadPrefixDataMessage(
                    payload_base, byte_reader)
            elif prefix_type == EIEIOPrefix.LOWER_HALF_WORD:
                return EIEIO32BitTimedPayloadPrefixLowerKeyPrefixDataMessage(
                    prefix, payload_base, byte_reader)
            elif prefix_type == EIEIOPrefix.UPPER_HALF_WORD:
                return EIEIO32BitTimedPayloadPrefixUpperKeyPrefixDataMessage(
                    prefix, payload_base, byte_reader)
        return EIEIODataMessage(eieio_header, byte_reader)

    @staticmethod
    def _read_32_bit_payload_message(prefix, payload_base, prefix_type,
                                     is_time, byte_reader, eieio_header):
        if payload_base is None and not is_time:
            if prefix is None:
                return EIEIO32BitWithPayloadDataMessage(byte_reader)
            elif prefix_type == EIEIOPrefix.LOWER_HALF_WORD:
                return EIEIO32BitWithPayloadLowerKeyPrefixDataMessage(
                    prefix, byte_reader)
            elif prefix_type == EIEIOPrefix.UPPER_HALF_WORD:
                return EIEIO32BitWithPayloadUpperKeyPrefixDataMessage(
                    prefix, byte_reader)
        elif payload_base is not None and not is_time:
            if prefix is None:
                return EIEIO32BitWithPayloadPayloadPrefixDataMessage(
                    payload_base, byte_reader)
            elif prefix_type == EIEIOPrefix.LOWER_HALF_WORD:
                return EIEIO32BitWithPayloadPayloadPrefixLowerKeyPrefixDataMessage(
                    prefix, payload_base, byte_reader)
            elif prefix_type == EIEIOPrefix.UPPER_HALF_WORD:
                return EIEIO32BitWithPayloadPayloadPrefixUpperKeyPrefixDataMessage(
                    prefix, payload_base, byte_reader)
        elif payload_base is None and is_time:
            if prefix is None:
                return EIEIO32BitWithPayloadTimedDataMessage(byte_reader)
            elif prefix_type == EIEIOPrefix.LOWER_HALF_WORD:
                return EIEIO32BitWithPayloadTimedLowerKeyPrefixDataMessage(
                    prefix, byte_reader)
            elif prefix_type == EIEIOPrefix.UPPER_HALF_WORD:
                return EIEIO32BitWithPayloadTimedUpperKeyPrefixDataMessage(
                    prefix, byte_reader)
        return EIEIODataMessage(eieio_header, byte_reader)

    @staticmethod
    def read_eieio_message(byte_reader):
        eieio_header = EIEIODataHeader.read_eieio_header(byte_reader)
        eieio_type = eieio_header.eieio_type
        prefix = eieio_header.prefix
        payload_base = eieio_header.payload_base
        prefix_type = eieio_header.prefix_type
        is_time = eieio_header.is_time
        if eieio_type == EIEIOType.KEY_16_BIT:
            return EIEIODataMessage._read_16_bit_message(
                prefix, payload_base, prefix_type, is_time, byte_reader,
                eieio_header)
        elif eieio_type == EIEIOType.KEY_PAYLOAD_16_BIT:
            return EIEIODataMessage._read_16_bit_payload_message(
                prefix, payload_base, prefix_type, is_time, byte_reader,
                eieio_header)
        elif eieio_type == EIEIOType.KEY_32_BIT:
            return EIEIODataMessage._read_32_bit_message(
                prefix, payload_base, prefix_type, is_time, byte_reader,
                eieio_header)
        elif eieio_type == EIEIOType.KEY_PAYLOAD_32_BIT:
            return EIEIODataMessage._read_32_bit_payload_message(
                prefix, payload_base, prefix_type, is_time, byte_reader,
                eieio_header)
        return EIEIODataMessage(eieio_header, byte_reader)

    def __str__(self):
        if self._data_reader is not None:
            return "EIEIODataMessage:{}:{}".format(
                self._eieio_header, self._eieio_header.count)
        return "EIEIODataMessage:{}:{}".format(
            self._eieio_header, self._elements)

    def __repr__(self):
        return self.__str__()
