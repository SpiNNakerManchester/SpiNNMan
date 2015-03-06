from spinnman.messages.eieio.abstract_eieio_message import AbstractEIEIOMessage
from spinnman.messages.eieio.eieio_command_header import EIEIOCommandHeader
from spinnman.data.little_endian_byte_array_byte_writer import \
    LittleEndianByteArrayByteWriter
from spinnman import exceptions

import binascii


class EIEIOCommandMessage(AbstractEIEIOMessage):

    def __init__(self, eieio_command_header, data=None):
        if data is None:
            data = bytearray()
        
        AbstractEIEIOMessage.__init__(self, data)
        if isinstance(eieio_command_header, EIEIOCommandHeader):
            self._eieio_command_header = eieio_command_header
        else:
            raise exceptions.SpinnmanInvalidParameterException(
                "eieio_command_header", "invalid",
                "the header is not a eieio command header, therefore error has"
                "been raised")
    @property
    def eieio_command_header(self):
        return self._eieio_command_header

    def is_EIEIO_message(self):
        return True

    def add_data(self, data):
        """ Adds a byte array data onto the command's data

        :param data: the data to add
        :type data: bytearray
        """
        writer = LittleEndianByteArrayByteWriter()
        writer.write_bytes(data)
        self._data.extend(writer.data)

    def convert_to_byte_array(self):
        """ converts the command message into a byte array in little endian form

        :return:the byte array which represents the command message
        """
        writer = LittleEndianByteArrayByteWriter()
        self._eieio_command_header.write_command_header(writer)
        if self._data is not None:
            writer.write_bytes(self._data)
        return writer.data

    def __str__(self):
        return "{}:{}".format(self._eieio_command_header,
                              binascii.hexlify(self._data))

    def __repr__(self):
        return self.__str__()
