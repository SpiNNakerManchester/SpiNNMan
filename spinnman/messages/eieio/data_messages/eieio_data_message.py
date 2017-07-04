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

import math
import struct


class EIEIODataMessage(AbstractEIEIOMessage):
    """ An EIEIO Data message
    """

    def __init__(self, eieio_header, data=None, offset=0):
        """

        :param eieio_header: The header of the message
        :type eieio_header:\
                    :py:class:`spinnman.messages.eieio.data_messages.eieio_data_header.EIEIODataHeader`
        :param data: Optional data contained within the packet
        :type data: str
        :param offset: Optional offset where the valid data starts
        :type offset: int
        """

        # The header
        self._eieio_header = eieio_header

        # Elements to be written
        self._elements = b""

        # Keeping track of the reading of the data
        self._data = data
        self._offset = offset
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
                    read data
        """
        if self._data is not None:
            raise SpinnmanInvalidPacketException(
                "EIEIODataMessage", "This packet is read-only")

        self._elements += element.get_bytestring(self._eieio_header.eieio_type)
        self._eieio_header.increment_count()

    @property
    def is_next_element(self):
        """ Determine if there is another element to be read

        :return: True if the message was created with data, and there are more\
                    elements to be read
        :rtype: bool
        """
        return (self._data is not None and
                self._elements_read < self._eieio_header.count)

    @property
    def next_element(self):
        """ The next element to be read, or None if no more elements.  The\
            exact type of element returned depends on the packet type

        :rtype:\
                    :py:class:`spinnman.messages.eieio.data_messages.abstract_eieio_data_element.AbstractEIEIODataElement`
        """
        if not self.is_next_element:
            return None
        self._elements_read += 1
        key = None
        payload = None
        if self._eieio_header.eieio_type == EIEIOType.KEY_16_BIT:
            key = struct.unpack_from("<H", self._data, self._offset)[0]
            self._offset += 2
        if self._eieio_header.eieio_type == EIEIOType.KEY_32_BIT:
            key = struct.unpack_from("<I", self._data, self._offset)[0]
            self._offset += 4
        if self._eieio_header.eieio_type == EIEIOType.KEY_PAYLOAD_16_BIT:
            key, payload = struct.unpack_from("<HH", self._data, self._offset)
            self._offset += 4
        if self._eieio_header.eieio_type == EIEIOType.KEY_PAYLOAD_32_BIT:
            key, payload = struct.unpack_from("<II", self._data, self._offset)
            self._offset += 8

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

    @property
    def bytestring(self):
        return self._eieio_header.bytestring + self._elements

    def __str__(self):
        if self._data is not None:
            return "EIEIODataMessage:{}:{}".format(
                self._eieio_header, self._eieio_header.count)
        return "EIEIODataMessage:{}:{}".format(
            self._eieio_header, self._elements)

    def __repr__(self):
        return self.__str__()
