# Copyright (c) 2015 The University of Manchester
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import struct
from typing import Optional
from spinn_utilities.overrides import overrides
from spinnman.exceptions import (
    SpinnmanInvalidPacketException, SpinnmanInvalidParameterException)
from spinnman.messages.eieio import (
    AbstractEIEIOMessage, EIEIOType, EIEIOPrefix)
from spinnman.constants import UDP_MESSAGE_MAX_SIZE
from .eieio_data_header import EIEIODataHeader
from .key_data_element import KeyDataElement
from .key_payload_data_element import KeyPayloadDataElement
from .abstract_data_element import AbstractDataElement

_ONE_SHORT = struct.Struct("<H")
_TWO_SHORTS = struct.Struct("<HH")
_ONE_WORD = struct.Struct("<I")
_TWO_WORDS = struct.Struct("<II")


class EIEIODataMessage(AbstractEIEIOMessage):
    """
    An EIEIO Data message.
    """
    __slots__ = (
        "_data",
        "_elements",
        "_elements_read",
        "_header",
        "_offset")

    def __init__(self, eieio_header: EIEIODataHeader,
                 data: Optional[bytes] = None, offset: int = 0):
        """
        :param eieio_header: The header of the message
        :param data: Optional data contained within the packet
        :param offset: Optional offset where the valid data starts
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
            eieio_type: EIEIOType, count: int = 0,
            data: Optional[bytes] = None, offset: int = 0,
            key_prefix: Optional[int] = None,
            payload_prefix: Optional[int] = None,
            timestamp: Optional[int] = None,
            prefix_type: EIEIOPrefix = EIEIOPrefix.LOWER_HALF_WORD
            ) -> "EIEIODataMessage":
        """
        Create a data message.

        :param eieio_type: The type of the message
        :param count: The number of items in the message
        :param data: The data in the message
        :param offset:
            The offset in the data where the actual data starts
        :param key_prefix: The prefix of the keys
        :param payload_prefix: The prefix of the payload
        :param timestamp: The timestamp of the packet
        :param prefix_type: The type of the key prefix if 16-bits
        """
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
    @overrides(AbstractEIEIOMessage.eieio_header)
    def eieio_header(self) -> EIEIODataHeader:
        return self._header

    @staticmethod
    def min_packet_length(
            eieio_type: EIEIOType, is_prefix: bool = False,
            is_payload_base: bool = False, is_timestamp: bool = False) -> int:
        """
        The minimum length of a message with the given header, in bytes.

        :param eieio_type: the type of message
        :param is_prefix: True if there is a prefix, False otherwise
        :param is_payload_base:
            True if there is a payload base, False otherwise
        :param is_timestamp:
            True if there is a timestamp, False otherwise
        :return: The minimum size of the packet in bytes
        """
        header_size = EIEIODataHeader.get_header_size(
            eieio_type, is_prefix, is_payload_base | is_timestamp)
        return header_size + eieio_type.payload_bytes

    def get_min_packet_length(self) -> int:
        """ Get the minimum length of a message instance in bytes. """
        return self.min_packet_length(
            eieio_type=self._header.eieio_type,
            is_prefix=self._header.prefix is not None,
            is_payload_base=self._header.payload_base is not None)

    @property
    def max_n_elements(self) -> int:
        """ The maximum number of elements that can fit in the packet. """
        ty = self._header.eieio_type
        return (UDP_MESSAGE_MAX_SIZE - self._header.size) // (
            ty.key_bytes + ty.payload_bytes)

    @property
    def n_elements(self) -> int:
        """ The number of elements in the packet. """
        return self._header.count

    @property
    def size(self) -> int:
        """ The size of the packet with the current contents. """
        ty = self._header.eieio_type
        return (self._header.size +
                (ty.key_bytes + ty.payload_bytes) * self._header.count)

    def add_key_and_payload(self, key: int, payload: int) -> None:
        """
        Adds a key and payload to the packet.

        :param key: The key to add
        :param payload: The payload to add
        :raise SpinnmanInvalidParameterException:
            If the key or payload is too big for the format, or the format
            doesn't expect a payload
        """
        if key > self._header.eieio_type.max_value:
            raise SpinnmanInvalidParameterException(
                "key", key, "Larger than the maximum allowed of "
                f"{self._header.eieio_type.max_value}")
        if payload > self._header.eieio_type.max_value:
            raise SpinnmanInvalidParameterException(
                "payload", payload, "Larger than the maximum allowed of "
                f"{self._header.eieio_type.max_value}")

        self.add_element(KeyPayloadDataElement(
            key, payload, self._header.is_time))

    def add_key(self, key: int) -> None:
        """
        Add a key to the packet.

        :param key: The key to add
        :raise SpinnmanInvalidParameterException:
            If the key is too big for the format, or the format expects a
            payload
        """
        if key > self._header.eieio_type.max_value:
            raise SpinnmanInvalidParameterException(
                "key", key, "Larger than the maximum allowed of "
                f"{self._header.eieio_type.max_value}")
        self.add_element(KeyDataElement(key))

    def add_element(self, element: AbstractDataElement) -> None:
        """
        Add an element to the message.  The correct type of element must
        be added, depending on the header values.

        :param element: The element to be added
        :raise SpinnmanInvalidParameterException:
            If the element is not compatible with the header
        :raise SpinnmanInvalidPacketException:
            If the message was created to read data
        """
        if self._data is not None:
            raise SpinnmanInvalidPacketException(
                "EIEIODataMessage", "This packet is read-only")

        self._elements += element.get_bytestring(self._header.eieio_type)
        self._header.increment_count()

    @property
    def is_next_element(self) -> bool:
        """ Whether there is another element to be read. """
        return (self._data is not None and
                self._elements_read < self._header.count)

    @property
    def next_element(self) -> Optional[AbstractDataElement]:
        """
        The next element to be read, or `None` if no more elements.
        The exact type of element returned depends on the packet type.
        """
        if not self.is_next_element:
            return None
        self._elements_read += 1
        payload: Optional[int] = None
        assert self._data is not None
        if self._header.eieio_type == EIEIOType.KEY_16_BIT:
            key = _ONE_SHORT.unpack_from(self._data, self._offset)[0]
            self._offset += 2
        elif self._header.eieio_type == EIEIOType.KEY_32_BIT:
            key = _ONE_WORD.unpack_from(self._data, self._offset)[0]
            self._offset += 4
        elif self._header.eieio_type == EIEIOType.KEY_PAYLOAD_16_BIT:
            key, payload = _TWO_SHORTS.unpack_from(self._data, self._offset)
            self._offset += 4
        elif self._header.eieio_type == EIEIOType.KEY_PAYLOAD_32_BIT:
            key, payload = _TWO_WORDS.unpack_from(self._data, self._offset)
            self._offset += 8
        else:
            raise ValueError(
                f"unknown EIEIO type code: {self._header.eieio_type}")

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
    @overrides(AbstractEIEIOMessage.bytestring)
    def bytestring(self) -> bytes:
        return self._header.bytestring + self._elements

    def __str__(self) -> str:
        if self._data is not None:
            return f"EIEIODataMessage:{self._header}:{self._header.count}"
        return f"EIEIODataMessage:{self._header}:{self._elements!r}"

    def __repr__(self) -> str:
        return self.__str__()
