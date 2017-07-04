from spinnman.messages.eieio import EIEIOType, EIEIOPrefix
from spinnman.exceptions import SpinnmanInvalidPacketException
import struct


class EIEIODataHeader(object):

    def __init__(self, eieio_type, tag=0, prefix=None,
                 prefix_type=EIEIOPrefix.LOWER_HALF_WORD,
                 payload_base=None, is_time=False, count=0):
        """ EIEIO header for data packets

        :param eieio_type: the type of message
        :type eieio_type:\
                    :py:class:`spinnman.spinnman.messages.eieio.eieio_type.EIEIOType`
        :param tag: the tag of the message (0 by default)
        :type tag: int
        :param prefix: the key prefix of the message or None if not prefixed
        :type prefix: int or None
        :param prefix_type: the position of the prefix (upper or lower)
        :type prefix_type:\
                    :py:class:`spinnman.messages.eieio.eieio_prefix.EIEIOPrefix`
        :param payload_base: The base payload to be applied, or None if no\
                    base payload
        :type payload_base: int or None
        :param is_time: True if the payloads should be taken to be timestamps,\
                    or False otherwise
        :type is_time: bool
        :param count: Count of the number of items in the packet
        :type count: int
        """
        self._eieio_type = eieio_type
        self._tag = tag
        self._prefix = prefix
        self._prefix_type = prefix_type
        self._payload_base = payload_base
        self._is_time = is_time
        self._count = count

    @property
    def eieio_type(self):
        return self._eieio_type

    @property
    def tag(self):
        return self._tag

    @property
    def prefix(self):
        return self._prefix

    @property
    def prefix_type(self):
        return self._prefix_type

    @property
    def payload_base(self):
        return self._payload_base

    @property
    def is_time(self):
        return self._is_time

    @property
    def count(self):
        return self._count

    @count.setter
    def count(self, count):
        self._count = count

    @property
    def size(self):
        return EIEIODataHeader.get_header_size(
            self._eieio_type, self._prefix is not None,
            self._payload_base is not None)

    @staticmethod
    def get_header_size(eieio_type, is_prefix=False, is_payload_base=False):
        """ Get the size of a header with the given parameters

        :param eieio_type: the type of message
        :type eieio_type:\
                    :py:class:`spinnman.spinnman.messages.eieio.eieio_type.EIEIOType`
        :param is_prefix: True if there is a prefix, False otherwise
        :type is_prefix: bool
        :param is_payload_base: True if there is a payload base, False\
                    otherwise
        :type is_payload_base: bool
        :return: The size of the header in bytes
        :rtype: int
        """
        size = 2
        if is_prefix:
            size += 2
        if is_payload_base:
            size += eieio_type.key_bytes
        return size

    def increment_count(self):
        self._count += 1

    def reset_count(self):
        self._count = 0

    @property
    def bytestring(self):
        """ Get a bytestring of the header

        :return: The header as a bytestring
        :rtype: str
        """

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
        if self._payload_base is not None:
            if (self._eieio_type == EIEIOType.KEY_PAYLOAD_16_BIT or
                    self._eieio_type == EIEIOType.KEY_16_BIT):
                if self._prefix is not None:
                    return struct.pack(
                        "<BBHH", self._count, data, self._prefix,
                        self._payload_base)
                else:
                    return struct.pack(
                        "<BBH", self._count, data, self._payload_base)
            elif (self._eieio_type == EIEIOType.KEY_PAYLOAD_32_BIT or
                    self._eieio_type == EIEIOType.KEY_32_BIT):
                if self._prefix is not None:
                    return struct.pack(
                        "<BBHI", self._count, data, self._prefix,
                        self._payload_base)
                else:
                    return struct.pack(
                        "<BBI", self._count, data, self._payload_base)
        else:
            if self._prefix is not None:
                return struct.pack(
                    "<BBH", self._count, data, self._prefix)
            else:
                return struct.pack(
                    "<BB", self._count, data)

    @staticmethod
    def from_bytestring(data, offset):
        """ Read an eieio data header from a bytestring

        :param data: The bytestring to be read
        :type data: str
        :param offset: The offset at which the data starts
        :type offset: int
        :return: an EIEIO header
        :rtype:\
                    :py:class:`spinnman.messages.eieio.data_messages.eieio_data_header.EIEIODataHeader`
        """

        (count, header_data) = struct.unpack_from("<BB", data, offset)

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
                    (prefix, payload_prefix) = struct.unpack_from(
                        "<HH", data, offset + 2)
                else:
                    payload_prefix = struct.unpack_from(
                        "<H", data, offset + 2)[0]
            elif (eieio_type == EIEIOType.KEY_32_BIT or
                    eieio_type == EIEIOType.KEY_PAYLOAD_32_BIT):
                if prefix_flag == 1:
                    (prefix, payload_prefix) = struct.unpack_from(
                        "<HI", data, offset + 2)
                else:
                    payload_prefix = struct.unpack_from(
                        "<I", data, offset + 2)[0]
        else:
            if prefix_flag == 1:
                prefix = struct.unpack_from("<H", data, offset + 2)[0]

        return EIEIODataHeader(
            eieio_type=eieio_type, tag=tag, prefix=prefix,
            prefix_type=prefix_type, payload_base=payload_prefix,
            is_time=bool(payload_is_timestamp), count=count)

    def __str__(self):
        return ("EIEIODataHeader:prefix={}:prefix_type={}:payload_base={}:"
                "is_time={}:type={}:tag={}:count={}".format(
                    self._prefix, self._prefix_type, self._payload_base,
                    self._is_time, self._type.value, self._tag,
                    self._count))

    def __repr__(self):
        return self.__str__()
