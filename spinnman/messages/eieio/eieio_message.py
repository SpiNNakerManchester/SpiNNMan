from spinnman.data.little_endian_byte_array_byte_writer import \
    LittleEndianByteArrayByteWriter
from spinnman.messages.eieio.abstract_eieio_message import AbstractEIEIOMessage
from spinnman.messages.eieio.eieio_header import EIEIOHeader
from spinnman.messages.eieio.eieio_type_param import EIEIOTypeParam
from spinnman import exceptions
import struct
import binascii


class EIEIOMessage(AbstractEIEIOMessage):

    def __init__(self, eieio_header, data=None):
        if data is None:
            data = bytearray()
        AbstractEIEIOMessage.__init__(self, data)
        if isinstance(eieio_header, EIEIOHeader):
            self._eieio_header = eieio_header
            self._eieio_header.reset_count_param()
        else:
            raise exceptions.SpinnmanInvalidParameterException(
                "eieio_header", "invalid", "The header is not a eieio header, "
                                           "therefore error has been raised")

    @property
    def eieio_header(self):
        return self._eieio_header
    
    def is_EIEIO_message(self):
        return True

    @property
    def data(self):
        return self._data

    def write_data(self, key, payload=None):
        if key is None:
            raise exceptions.SpinnmanInvalidParameterException(
                "The key to be added cannot be None. Please correct the key "
                "and try again", "", "")
        if (self._eieio_header.type_param == EIEIOTypeParam.KEY_PAYLOAD_16_BIT or
                self._eieio_header.type_param == EIEIOTypeParam.KEY_PAYLOAD_32_BIT):
            if payload is None:
                raise exceptions.SpinnmanInvalidParameterException(
                    "The payload to be added cannot be None. Please correct "
                    "the payload and try again", "", "")
        else:
            if payload is not None:
                raise exceptions.SpinnmanInvalidParameterException(
                    "Cannot add a payload to a message type that does not "
                    "support payloads. Please change the message type and "
                    "try again", "", "")

        self._write_key(key)
        if payload is not None:
            self._write_payload(payload)

        self._eieio_header.increment_count_param()

    def _write_key(self, key):
        if (self._eieio_header.type_param == EIEIOTypeParam.KEY_16_BIT
                or self._eieio_header.type_param == EIEIOTypeParam.KEY_PAYLOAD_16_BIT):
            self._data += bytearray(struct.pack("<H", key))
        else:
            self._data += bytearray(struct.pack("<I", key))

    def _write_payload(self, payload):
        if self._eieio_header.type_param == EIEIOTypeParam.KEY_PAYLOAD_16_BIT:
            self._data += bytearray(struct.pack("<H", payload))
        else:
            self._data += bytearray(struct.pack("<I", payload))

    def convert_to_byte_array(self):
        """ converts the eieio data message into a byte array in little endian
        form

        :return:the byte array which represents the command message
        """
        writer = LittleEndianByteArrayByteWriter()
        self._eieio_header.write_eieio_header(writer)

        return writer.data + self._data

    @staticmethod
    def create_eieio_messages_from(buffer_data):
        """this method takes a collection of buffers in the form of a single
        byte array and interprets them as eieio messages and returns a list of
        eieio messages

        :param buffer_data: the byte array data
        :type buffer_data: LittleEndianByteArrayByteReader
        :rtype: list of EIEIOMessages
        :return: a list containing EIEIOMessages
        """
        messages = list()
        while not buffer_data.is_at_end():
            eieio_header = EIEIOHeader.create_header_from_reader(buffer_data)
            message = EIEIOMessage.create_eieio_message_from(eieio_header,
                                                             buffer_data)
            messages.append(message)
        return messages

    @staticmethod
    def create_eieio_message_from(eieio_header, buffer_data):
        """this method takes a collection of buffers in the form of a single
        byte array, a fully formed eieio header and a position in the byte array
         and interprets them as a fully formed eieio message

        :param buffer_data: the byte array data
        :type buffer_data: LittleEndianByteArrayByteReader
        :param eieio_header: the eieio header which informs the method how to
                             interprets the buffer data
        :type eieio_header: EIEIOHeader
        :rtype: EIEIOMessage
        :return: a EIEIOMessage
        """
        each_piece_of_data = 0
        if eieio_header.type_param == EIEIOTypeParam.KEY_16_BIT:
            each_piece_of_data += 2
        elif eieio_header.type_param == EIEIOTypeParam.KEY_32_BIT:
            each_piece_of_data += 4
        elif eieio_header.type_param == EIEIOTypeParam.KEY_PAYLOAD_16_BIT:
            each_piece_of_data += 4
        elif eieio_header.type_param == EIEIOTypeParam.KEY_PAYLOAD_32_BIT:
            each_piece_of_data += 8
        else:
            raise exceptions.SpinnmanInvalidPacketException(
                "eieio_header.type_param", "invalid")

        data_to_read = eieio_header.count_param * each_piece_of_data

        data = buffer_data.read_bytes(data_to_read)
        return EIEIOMessage(eieio_header, data)

    def __str__(self):
        return "{}:{}".format(self._eieio_header, binascii.hexlify(self._data))

    def __repr__(self):
        return self.__str__()
