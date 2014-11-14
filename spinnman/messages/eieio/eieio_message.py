from spinnman.messages.eieio.abstract_eieio_message import AbstractEIEIOMessage
from spinnman.messages.eieio.eieio_header import EIEIOHeader
from spinnman.messages.eieio.eieio_type_param import EIEIOTypeParam
from spinnman import exceptions
import struct
import binascii


class EIEIOMessage(AbstractEIEIOMessage):

    def __init__(self, eieio_header, data=bytearray()):
        AbstractEIEIOMessage.__init__(self, data)
        if isinstance(eieio_header, EIEIOHeader):
            self._eieio_header = eieio_header
        else:
            raise exceptions.SpinnmanInvalidParameterException(
                "eieio_header", "invalid", "The header is not a eieio header, "
                                           "therefore error has been raised")

    @property
    def eieio_header(self):
        return self._eieio_header
    
    def is_EIEIO_message(self):
        return True

    def write_key(self, key):
        if key is None:
            raise exceptions.SpinnmanInvalidParameterException(
                "The key to be added cannot be None. Please correct the key "
                "and try again", "", "")
        if (self._eieio_header.type_param == EIEIOTypeParam.KEY_16_BIT
                or self._eieio_header.type_param == EIEIOTypeParam.KEY_PAYLOAD_16_BIT):
            self._data += bytearray(struct.pack("<H", key))
        else:
            self._data += bytearray(struct.pack("<I", key))

    def _write_payload(self, payload):
        if payload is None:
            raise exceptions.SpinnmanInvalidParameterException(
                "The payload to be added cannot be None. Please correct the "
                "payload and try again", "", "")
        if self._eieio_header.type_param == EIEIOTypeParam.KEY_PAYLOAD_16_BIT:
            self._data += bytearray(struct.pack("<H", payload))
        elif self._eieio_header.type_param == EIEIOTypeParam.KEY_PAYLOAD_32_BIT:
            self._data += bytearray(struct.pack("<I", payload))
        else:
            raise exceptions.SpinnmanInvalidParameterException(
                "Cannot add a payload to a message type that does not support "
                "payloads. Please change the message type and try again", "",
                "")

    def write_key_and_payload(self, key, payload):
        self.write_key(key)
        self._write_payload(payload)

    @staticmethod
    def create_eieio_messages_from(buffer_data):
        """this method takes a collection of buffers in the form of a single
        byte array and interpretes them as eieio messages and returns a list of
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
         and interpretes them as a fully formed eieio message

        :param buffer_data: the byte array data
        :type buffer_data: LittleEndianByteArrayByteReader
        :param eieio_header: the eieio header which informs the method how to
                             interprete the buffer data
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
