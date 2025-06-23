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

from spinnman.messages.eieio import EIEIOType, EIEIOPrefix
from spinnman.exceptions import SpinnmanInvalidPacketException

_PATTERN_BBHH = struct.Struct("<BBHH")
_PATTERN_BBH = struct.Struct("<BBH")
_PATTERN_BBHI = struct.Struct("<BBHI")
_PATTERN_BBI = struct.Struct("<BBI")
_PATTERN_BB = struct.Struct("<BB")
_PATTERN_HH = struct.Struct("<HH")
_PATTERN_H = struct.Struct("<H")
_PATTERN_HI = struct.Struct("<HI")
_PATTERN_I = struct.Struct("<I")


class EIEIODataHeader(object):
    """
    The header part of EIEIO data.
    """
    __slots__ = (
        "_count",
        "_eieio_type",
        "_is_time",
        "_payload_base",
        "_prefix",
        "_prefix_type",
        "_tag")

    def __init__(self, eieio_type: EIEIOType, tag: int = 0,
                 prefix: Optional[int] = None,
                 prefix_type: EIEIOPrefix = EIEIOPrefix.LOWER_HALF_WORD,
                 payload_base: Optional[int] = None, is_time: bool = False,
                 count: int = 0):
        """
        EIEIO header for data packets.

        :param eieio_type: the type of message
        :param tag: the tag of the message (0 by default)
        :param prefix: the key prefix of the message or `None` if not prefixed
        :param prefix_type:
            the position of the prefix (upper or lower)
        :param payload_base:
            The base payload to be applied, or `None` if no base payload
        :param is_time:
            True if the payloads should be taken to be timestamps, or False
            otherwise
        :param count: Count of the number of items in the packet
        """
        self._eieio_type = eieio_type
        self._tag = tag
        self._prefix = prefix
        self._prefix_type = prefix_type
        self._payload_base = payload_base
        self._is_time = is_time
        self._count = count

    @property
    def eieio_type(self) -> EIEIOType:
        """
        Gets the eieio_type passed into the init."""
        return self._eieio_type

    @property
    def tag(self) -> int:
        """
        Gets the tag value passed into the init. """
        return self._tag

    @property
    def prefix(self) -> Optional[int]:
        """
        Gets prefix passed into the init (if applicable). """
        return self._prefix

    @property
    def prefix_type(self) -> EIEIOPrefix:
        """
        Gets the prefix_type passed into the init. """
        return self._prefix_type

    @property
    def payload_base(self) -> Optional[int]:
        """
        Gets the payload_base value passed into the init (if applicable). """
        return self._payload_base

    @property
    def is_time(self) -> bool:
        """
        Gets the is_time value passed into the init. """
        return self._is_time

    @property
    def count(self) -> int:
        """
        Count of the number of items in the packet """
        return self._count

    @count.setter
    def count(self, count: int) -> None:
        """
        Sets the Count of the number of items in the packet

        :param count: the new value
        """
        self._count = count

    @property
    def size(self) -> int:
        """
        Get the size of a header with the given parameters. """
        return EIEIODataHeader.get_header_size(
            self._eieio_type, self._prefix is not None,
            self._payload_base is not None)

    @staticmethod
    def get_header_size(eieio_type: EIEIOType, is_prefix: bool = False,
                        is_payload_base: bool = False) -> int:
        """
        Get the size of a header with the given parameters.

        :param eieio_type: the type of message
        :param is_prefix: True if there is a prefix, False otherwise
        :param is_payload_base:
            True if there is a payload base, False otherwise
        :return: The size of the header in bytes
        """
        size = 2
        if is_prefix:
            size += 2
        if is_payload_base:
            size += eieio_type.key_bytes
        return size

    def increment_count(self) -> None:
        """
        Increase the count by 1.
        """
        self._count += 1

    def reset_count(self) -> None:
        """
        Resets the count back to zero.
        """
        self._count = 0

    @property
    def bytestring(self) -> bytes:
        """
        The byte-string of the header. """
        # Convert the flags to an int
        data = 0

        # the flag for prefix or not
        if self._prefix is not None:
            data |= 1 << 7

            # the prefix type
            data |= self._prefix_type.value << 6

        # the flag for payload prefix
        if self._payload_base is not None:
            data |= 1 << 5

        # the flag for time in payloads
        if self._is_time:
            data |= 1 << 4

        # The type of the packet
        data |= self._eieio_type.value << 2

        # The tag of the packet
        data |= self._tag

        # Convert the remaining data, depending on the various options
        if self._payload_base is None:
            if self._prefix is not None:
                return _PATTERN_BBH.pack(self._count, data, self._prefix)
            return _PATTERN_BB.pack(self._count, data)
        if (self._eieio_type == EIEIOType.KEY_PAYLOAD_16_BIT or
                self._eieio_type == EIEIOType.KEY_16_BIT):
            if self._prefix is not None:
                return _PATTERN_BBHH.pack(
                    self._count, data, self._prefix, self._payload_base)
            return _PATTERN_BBH.pack(self._count, data, self._payload_base)
        if (self._eieio_type == EIEIOType.KEY_PAYLOAD_32_BIT or
                self._eieio_type == EIEIOType.KEY_32_BIT):
            if self._prefix is not None:
                return _PATTERN_BBHI.pack(
                    self._count, data, self._prefix, self._payload_base)
            return _PATTERN_BBI.pack(self._count, data, self._payload_base)
        raise SpinnmanInvalidPacketException(
            "EIEIODataMessage", "unexpected EIEIO type code")

    @staticmethod
    def from_bytestring(data: bytes, offset: int) -> 'EIEIODataHeader':
        """
        Read an EIEIO data header from a byte-string.

        :param data: The byte-string to be read
        :param offset: The offset at which the data starts
        :return: an EIEIO header
        """
        (count, header_data) = _PATTERN_BB.unpack_from(data, offset)

        # Read the flags in the header
        prefix_flag = (header_data >> 7) & 1
        format_flag = (header_data >> 6) & 1
        payload_prefix_flag = (header_data >> 5) & 1
        payload_is_timestamp = (header_data >> 4) & 1
        message_type = (header_data >> 2) & 3
        tag = header_data & 3

        # Check for command header
        if prefix_flag == 0 and format_flag == 1:
            raise SpinnmanInvalidPacketException(
                "EIEIODataHeader",
                "The header indicates that this is a command header")

        # Convert the flags into types
        eieio_type = EIEIOType(message_type)
        prefix_type = EIEIOPrefix(format_flag)

        prefix = None
        payload_prefix = None
        if payload_prefix_flag == 1:
            if (eieio_type == EIEIOType.KEY_16_BIT or
                    eieio_type == EIEIOType.KEY_PAYLOAD_16_BIT):
                if prefix_flag == 1:
                    (prefix, payload_prefix) = _PATTERN_HH.unpack_from(
                        data, offset + 2)
                else:
                    payload_prefix = _PATTERN_H.unpack_from(
                        data, offset + 2)[0]
            elif (eieio_type == EIEIOType.KEY_32_BIT or
                    eieio_type == EIEIOType.KEY_PAYLOAD_32_BIT):
                if prefix_flag == 1:
                    (prefix, payload_prefix) = _PATTERN_HI.unpack_from(
                        data, offset + 2)
                else:
                    payload_prefix = _PATTERN_I.unpack_from(
                        data, offset + 2)[0]
        else:
            if prefix_flag == 1:
                prefix = _PATTERN_H.unpack_from(data, offset + 2)[0]

        return EIEIODataHeader(
            eieio_type=eieio_type, tag=tag, prefix=prefix,
            prefix_type=prefix_type, payload_base=payload_prefix,
            is_time=bool(payload_is_timestamp), count=count)

    def __str__(self) -> str:
        return (f"EIEIODataHeader:prefix={self._prefix}:"
                f"prefix_type={self._prefix_type}:"
                f"payload_base={self._payload_base}:"
                "is_time={self._is_time}:type={self._eieio_type.value}:"
                "tag={self._tag}:count={self._count}")

    def __repr__(self) -> str:
        return self.__str__()
