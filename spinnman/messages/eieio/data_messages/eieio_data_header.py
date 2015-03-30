from spinnman.messages.eieio.eieio_type import EIEIOType
from spinnman.messages.eieio.eieio_prefix import EIEIOPrefix
from spinnman.exceptions import SpinnmanInvalidPacketException


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

    def write_eieio_header(self, byte_writer):
        """ Writes the header to a writer

        :param byte_writer: The writer to write the header to
        :type byte_writer:\
                    :py:class:`spinnman.data.abstract_byte_writer.AbstractByteWriter`
        """

        # write the count (header is little endian short so out of order)
        byte_writer.write_byte(self._count)

        # Write the flags into an int
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

        # Write the flags
        byte_writer.write_byte(data)

        # If there is a prefix, write the prefix
        if self._prefix is not None:
            byte_writer.write_short(self._prefix)

        # If there is a payload base, write the payload base
        if self._payload_base is not None:
            if (self._eieio_type == EIEIOType.KEY_PAYLOAD_16_BIT or
                    self._eieio_type == EIEIOType.KEY_16_BIT):
                byte_writer.write_short(self._payload_base)
            elif (self._eieio_type == EIEIOType.KEY_PAYLOAD_32_BIT or
                    self._eieio_type == EIEIOType.KEY_32_BIT):
                byte_writer.write_int(self._payload_base)

    @staticmethod
    def read_eieio_header(byte_reader):
        """ Read an eieio data header from a byte_reader

        :param byte_reader: The reader to read the data from
        :type byte_reader:\
                    :py:class:`spinnman.data.abstract_byte_reader.AbstractByteReader`
        :return: an eieio header
        :rtype:\
                    :py:class:`spinnman.messages.eieio.data_messages.eieio_data_header.EIEIODataHeader`
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    reading from the reader
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If there\
                    are too few bytes to read the header
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If there\
                    is an error setting any of the values
        """

        # Read the count of the header (little endian short so out of order)
        count = byte_reader.read_byte()

        # Read the flags in the header
        header_data = byte_reader.read_byte()
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
        if prefix_flag == 1:
            prefix = byte_reader.read_short()

        payload_prefix = None
        if payload_prefix_flag == 1:
            if (eieio_type == EIEIOType.KEY_16_BIT or
                    eieio_type == EIEIOType.KEY_PAYLOAD_16_BIT):
                payload_prefix = byte_reader.read_short()
            elif (eieio_type == EIEIOType.KEY_32_BIT or
                    eieio_type == EIEIOType.KEY_PAYLOAD_32_BIT):
                payload_prefix = byte_reader.read_int()

        header = EIEIODataHeader(
            eieio_type=eieio_type, tag=tag, prefix=prefix,
            prefix_type=prefix_type, payload_base=payload_prefix,
            is_time=bool(payload_is_timestamp), count=count)

        return header

    def __str__(self):
        return ("EIEIODataHeader:prefix={}:prefix_type={}:payload_base={}:"
                "is_time={}:type={}:tag={}:count={}".format(
                    self._prefix, self._prefix_type, self._payload_base,
                    self._is_time, self._type.value, self._tag,
                    self._count))

    def __repr__(self):
        return self.__str__()
