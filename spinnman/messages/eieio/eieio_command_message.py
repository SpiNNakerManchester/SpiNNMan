from spinnman.messages.eieio.abstract_eieio_message import AbstractEIEIOMessage
from spinnman.messages.eieio.eieio_command_header import EIEIOCommandHeader
from spinnman.data.little_endian_byte_array_byte_writer import \
    LittleEndianByteArrayByteWriter
from spinnman import exceptions

import binascii


class EIEIOCommandMessage(AbstractEIEIOMessage):

    def __init__(self, eieio_command_header, data):
        AbstractEIEIOMessage.__init__(self, data)
        if isinstance(eieio_command_header, EIEIOCommandHeader):
            self._eieio_command_header = eieio_command_header
        else:
            raise exceptions.SpinnmanInvalidParameterException(
                "eieio_command_header", "invaid",
                "the header is not a eieio command header, therefore error has"
                "been raised")
    @property
    def eieio_command_header(self):
        return self._eieio_command_header

    def is_EIEIO_message(self):
        return True

    def convert_to_byte_array(self):
        """ converts the command message into a byte array in little endian form

        :return:the byte array which represnets the command message
        """
        writer = LittleEndianByteArrayByteWriter()
        writer.write_short(self._eieio_command_header.write_command_header(writer))
        writer.write_bytes(self._data)
        return writer.data

    def __str__(self):
        return "{}:{}".format(self._eieio_command_header,
                              binascii.hexlify(self._data))

    def __repr__(self):
        return self.__str__()