# Copyright (c) 2017-2019 The University of Manchester
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import math
import struct
from spinnman.exceptions import (
    SpinnmanInvalidPacketException, SpinnmanInvalidParameterException)
from spinnman.messages.eieio import (
    AbstractEIEIOMessage, EIEIOType, EIEIOPrefix)
from spinnman.constants import UDP_MESSAGE_MAX_SIZE
from .eieio_data_header import EIEIODataHeader
from .key_data_element import KeyDataElement
from .key_payload_data_element import KeyPayloadDataElement

_ONE_SHORT = struct.Struct("<H")
_TWO_SHORTS = struct.Struct("<HH")
_ONE_WORD = struct.Struct("<I")
_TWO_WORDS = struct.Struct("<II")


class EIEIODataMessage(AbstractEIEIOMessage):
    """ An EIEIO Data message
    """
    __slots__ = [
        "_data",
        "_elements",
        "_elements_read",
        "_header",
        "_offset"]

    def __init__(self, eieio_header, data=None, offset=0):
        """
        :param eieio_header: The header of the message
        :type eieio_header:\
            :py:class:`spinnman.messages.eieio.data_messages.EIEIODataHeader`
        :param data: Optional data contained within the packet
        :type data: str
        :param offset: Optional offset where the valid data starts
        :type offset: int
        """

        # The header
        self._header = eieio_header

        # Elements to be written
        self._elements = b""

        # Keeping track of the reading of the data
        self._data = data
        self._offset = offset
        self._elements_read = 0

    @staticmethod
    def create(
            eieio_type, count=0, data=None, offset=0, key_prefix=None,
            payload_prefix=None, timestamp=None,
            prefix_type=EIEIOPrefix.LOWER_HALF_WORD):
        """ Create a data message

        :param eieio_type: The EIEIOType of the message
        :param count: The number of items in the message
        :param data: The data in the message
        :param offset: The offset in the data where the actual data starts
        :param key_prefix: The prefix of the keys
        :param payload_prefix: The prefix of the payload
        :param timestamp: The timestamp of the packet
        :param prefix_type: The type of the key prefix if 16-bits
        """
        # pylint: disable=too-many-arguments
        payload_base = payload_prefix
        if timestamp is not None:
            payload_base = timestamp
        return EIEIODataMessage(
            eieio_header=EIEIODataHeader(
                eieio_type, count=count, prefix=key_prefix,
                payload_base=payload_base, prefix_type=prefix_type,
                is_time=timestamp is not None),
            data=data, offset=offset)

    @property
    def eieio_header(self):
        return self._header

    @staticmethod
    def min_packet_length(
            eieio_type, is_prefix=False, is_payload_base=False,
            is_timestamp=False):
        """ The minimum length of a message with the given header, in bytes

        :param eieio_type: the type of message
        :type eieio_type:\
            :py:class:`spinnman.spinnman.messages.eieio.EIEIOType`
        :param is_prefix: True if there is a prefix, False otherwise
        :type is_prefix: bool
        :param is_payload_base: \
            True if there is a payload base, False otherwise
        :type is_payload_base: bool
        :param is_timestamp: True if there is a timestamp, False otherwise
        :return: The minimum size of the packet in bytes
        :rtype: int
        """
        header_size = EIEIODataHeader.get_header_size(
            eieio_type, is_prefix, is_payload_base | is_timestamp)
        return header_size + eieio_type.payload_bytes

    def get_min_packet_length(self):
        """ Get the minimum length of a message instance in bytes

        :rtype: int
        """
        return EIEIODataMessage.min_packet_length(
            eieio_type=self._header.eieio_type,
            is_prefix=self._header.prefix is not None,
            is_payload_base=self._header.payload_base is not None)

    @property
    def max_n_elements(self):
        """ The maximum number of elements that can fit in the packet

        :rtype: int
        """
        ty = self._header.eieio_type
        return int(math.floor(
            (UDP_MESSAGE_MAX_SIZE - self._header.size) /
            (ty.key_bytes + ty.payload_bytes)))

    @property
    def n_elements(self):
        """ The number of elements in the packet
        """
        return self._header.count

    @property
    def size(self):
        """ The size of the packet with the current contents
        """
        ty = self._header.eieio_type
        return (self._header.size +
                (ty.key_bytes + ty.payload_bytes) * self._header.count)

    def add_key_and_payload(self, key, payload):
        """ Adds a key and payload to the packet

        :param key: The key to add
        :type key: int
        :param payload: The payload to add
        :type payload: int
        :raise SpinnmanInvalidParameterException:\
            If the key or payload is too big for the format, or the format\
            doesn't expect a payload
        """
        if key > self._header.eieio_type.max_value:
            raise SpinnmanInvalidParameterException(
                "key", key,
                "Larger than the maximum allowed of {}".format(
                    self._header.eieio_type.max_value))
        if payload > self._header.eieio_type.max_value:
            raise SpinnmanInvalidParameterException(
                "payload", payload,
                "Larger than the maximum allowed of {}".format(
                    self._header.eieio_type.max_value))

        EIEIODataMessage.add_element(
            self, KeyPayloadDataElement(
                key, payload, self._header.is_time))

    def add_key(self, key):
        """ Add a key to the packet

        :param key: The key to add
        :type key: int
        :raise SpinnmanInvalidParameterException:\
            If the key is too big for the format, or the format expects a\
            payload
        """
        if key > self._header.eieio_type.max_value:
            raise SpinnmanInvalidParameterException(
                "key", key,
                "Larger than the maximum allowed of {}".format(
                    self._header.eieio_type.max_value))
        EIEIODataMessage.add_element(self, KeyDataElement(key))

    def add_element(self, element):
        """ Add an element to the message.  The correct type of element must\
            be added, depending on the header values

        :param element: The element to be added
        :type element:\
            :py:class:`spinnman.messages.eieio.data_messages.AbstractDataElement`
        :raise SpinnmanInvalidParameterException: \
            If the element is not compatible with the header
        :raise SpinnmanInvalidPacketException: \
            If the message was created to read data
        """
        if self._data is not None:
            raise SpinnmanInvalidPacketException(
                "EIEIODataMessage", "This packet is read-only")

        self._elements += element.get_bytestring(self._header.eieio_type)
        self._header.increment_count()

    @property
    def is_next_element(self):
        """ Determine if there is another element to be read

        :return: True if the message was created with data, and there are more\
            elements to be read
        :rtype: bool
        """
        return (self._data is not None and
                self._elements_read < self._header.count)

    @property
    def next_element(self):
        """ The next element to be read, or None if no more elements.  The\
            exact type of element returned depends on the packet type

        :rtype:\
            :py:class:`spinnman.messages.eieio.data_messages.AbstractDataElement`
        """
        if not self.is_next_element:
            return None
        self._elements_read += 1
        key = None
        payload = None
        if self._header.eieio_type == EIEIOType.KEY_16_BIT:
            key = _ONE_SHORT.unpack_from(self._data, self._offset)[0]
            self._offset += 2
        if self._header.eieio_type == EIEIOType.KEY_32_BIT:
            key = _ONE_WORD.unpack_from(self._data, self._offset)[0]
            self._offset += 4
        if self._header.eieio_type == EIEIOType.KEY_PAYLOAD_16_BIT:
            key, payload = _TWO_SHORTS.unpack_from(self._data, self._offset)
            self._offset += 4
        if self._header.eieio_type == EIEIOType.KEY_PAYLOAD_32_BIT:
            key, payload = _TWO_WORDS.unpack_from(self._data, self._offset)
            self._offset += 8

        if self._header.prefix is not None:
            if self._header.prefix_type == EIEIOPrefix.UPPER_HALF_WORD:
                key |= self._header.prefix << 16
            else:
                key = key | self._header.prefix

        if self._header.payload_base is not None:
            if payload is not None:
                payload |= self._header.payload_base
            else:
                payload = self._header.payload_base

        if payload is None:
            return KeyDataElement(key)
        return KeyPayloadDataElement(key, payload, self._header.is_time)

    @property
    def bytestring(self):
        return self._header.bytestring + self._elements

    def __str__(self):
        if self._data is not None:
            return "EIEIODataMessage:{}:{}".format(
                self._header, self._header.count)
        return "EIEIODataMessage:{}:{}".format(
            self._header, self._elements)

    def __repr__(self):
        return self.__str__()
