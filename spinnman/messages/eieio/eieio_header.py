from spinnman.messages.eieio.eieio_type_param import EIEIOTypeParam
from spinnman import exceptions
import struct


class EIEIOHeader(object):

    def __init__(self, type_param, count_param, tag_param=0, prefix_param=None,
                 payload_base=None, prefix_type=None, is_time=False):
        """the basic eieio header

        :param prefix_param: the prefix if needed, or None
        :param payload_base: the data to replace the prefix if not prefix set/
         or None
        :param type_param: the type of message format
        :param count_param: the count param
        :param tag_param: the tag being used or 0
        :param prefix_type: the position of the prefix (upper or lower)
        :param is_time: is the time param set
        :type prefix_param: int or None
        :type payload_base: int or None
        :type type_param: spinnman.spinnman.messages.eieio.eieio_type_param.EIEIOTypeParam
        :type count_param: int
        :type tag_param: int
        :type prefix_type: spinnman.spinnman.messages.eieio.eieio_prefix_type
        :type is_time: bool
        :return:
        """
        self._prefix_param = prefix_param
        self._payload_base = payload_base
        if not isinstance(type_param, EIEIOTypeParam):
            raise exceptions.SpinnmanInvalidParameterException(
                "the eieio type_param is not a valid EIEIOTypeParam", "", "")
        self._type_param = type_param
        self._count_param = count_param
        self._tag_param = tag_param
        self._prefix_type = prefix_type
        self._is_time = is_time

    @property
    def type_param(self):
        return self._type_param

    @property
    def prefix_param(self):
        return self._prefix_param

    @property
    def payload_base(self):
        return self._payload_base

    @property
    def count_param(self):
        return self._count_param

    @property
    def tag_param(self):
        return self._tag_param

    @property
    def prefix_type(self):
        return self._prefix_type

    @property
    def is_time(self):
        return self._is_time

    def write_eieio_header(self, byte_writer):
        #writes in little endian form
        #count param
        byte_writer.write_byte(self._count_param)

        data = 0
        # the flag for no prefix
        if self._prefix_param is not None:
            data |= 1 << 7  # the flag for prefix

        #the flag for packet format
        if self._prefix_type is not None:
            data |= self._prefix_type.value << 6

        #payload param
        if self._payload_base is not None:
            data |= 1 << 5  # the flag for payload prefix

        #time param
        if self._is_time:
            data |= 1 << 4  # the flag for time

        #type param
        data |= self._type_param.value << 2

        #tag param
        data |= self._tag_param
        byte_writer.write_byte(data)
        if self._prefix_param is not None:
            x = struct.pack("<H", self._prefix_param)
            y = bytearray(x)
            byte_writer.write_bytes(y)

        if self._payload_base is not None:
            if (self._type_param == EIEIOTypeParam.KEY_PAYLOAD_16_BIT
                    or self._type_param == EIEIOTypeParam.KEY_16_BIT):
                x = struct.pack("<H", self._payload_base)
                y = bytearray(x)
                byte_writer.write_bytes(y)
            elif (self._type_param == EIEIOTypeParam.KEY_PAYLOAD_32_BIT
                    or self._type_param == EIEIOTypeParam.KEY_32_BIT):
                x = struct.pack("<I", self._payload_base)
                y = bytearray(x)
                byte_writer.write_bytes(y)

    @staticmethod
    def create_header_from_reader(byte_reader):
        """ Read an eieio data header from a byte_reader

        :param byte_reader: The reader to read the data from
        :type byte_reader:\
                    :py:class:`spinnman.data.abstract_byte_reader.AbstractByteReader`
        :return: a eieio header
        :rtype: :py:class:`spinnman.data.eieio.eieio_header.EIEIOHeader`
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    reading from the reader
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If there\
                    are too few bytes to read the header
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If there\
                    is an error setting any of the values
        """
        count = byte_reader.read_byte()
        header_data = byte_reader.read_byte()
        p = (header_data >> 7) & 1
        f = (header_data >> 6) & 1
        d = (header_data >> 5) & 1
        t = (header_data >> 4) & 1

        message_type = (header_data >> 2) & 3
        tag = header_data & 3
        prefix = None
        if p == 1:
            prefix2 = byte_reader.read_byte()
            prefix1 = byte_reader.read_byte()
            prefix = (prefix1 << 8) | prefix2

        if f != 0:
            raise exceptions.SpinnmanInvalidPacketException(
                "eieio header", "the format param from the received packet is "
                                "invalid")
        if d == 1:
            if message_type == 0 or message_type == 1:  # 16 bits
                d2 = byte_reader.read_byte()
                d1 = byte_reader.read_byte()
                d = (d1 << 8) | d2
            elif message_type == 2 or message_type == 3:  # 32 bits
                d4 = byte_reader.read_byte()
                d3 = byte_reader.read_byte()
                d2 = byte_reader.read_byte()
                d1 = byte_reader.read_byte()
                d = (d4 << 24) | (d3 << 16) | (d1 << 8) | d2
            else:
                raise exceptions.SpinnmanInvalidPacketException(
                    "eieio header", "the type param from the received packet "
                                    "is invalid")

        if message_type == 0:
            message_type = EIEIOTypeParam.KEY_16_BIT
        elif message_type == 1:
            message_type = EIEIOTypeParam.KEY_PAYLOAD_16_BIT
        elif message_type == 2:
            message_type = EIEIOTypeParam.KEY_32_BIT
        elif message_type == 3:
            message_type = EIEIOTypeParam.KEY_PAYLOAD_32_BIT
        else:
            raise exceptions.SpinnmanInvalidPacketException(
                "eieio header", "the type param from the received packet is "
                                "invalid")

        return EIEIOHeader(
            type_param=message_type, count_param=count, tag_param=tag,
            prefix_param=prefix, payload_base=d, prefix_type=f, is_time=bool(t))

    def __str__(self):
        return "{}.{}.{}.{}.{}.{}.{}".format(
            self._prefix_param, self._prefix_type, self._payload_base,
            self._is_time, self._type_param.value, self._tag_param,
            self._count_param)

    def __repr__(self):
        return self.__str__()

