import struct
from enum import Enum
from spinnman.exceptions import SpinnmanInvalidParameterException

_ONE_SHORT = struct.Struct("<H")


class EIEIOCommandHeader(object):
    """ EIEIO header for command packets
    """
    __slots__ = [
        "_command"]

    def __init__(self, command):
        if isinstance(command, Enum):
            command = command.value
        if command < 0 or command >= 16384:
            raise SpinnmanInvalidParameterException(
                "command", command,
                "parameter command is outside the allowed range (0 to 16383)")
        self._command = command

    @property
    def command(self):
        return self._command

    @staticmethod
    def from_bytestring(data, offset):
        """ Read an EIEIO command header from a bytestring

        :param data: The bytestring to read the data from
        :type data: str or bytes
        :param offset: The offset where the valid data starts
        :type offset: int
        :return: an EIEIO command header
        :rtype:\
            :py:class:`EIEIOCommandHeader`
        :raise spinnman.exceptions.SpinnmanIOException: \
            If there is an error reading from the reader
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: \
            If there is an error setting any of the values
        """
        command_header = _ONE_SHORT.unpack_from(data, offset)[0]
        command = command_header & 0x3FFF

        return EIEIOCommandHeader(command)

    @property
    def bytestring(self):
        """ Get a bytestring of the header

        :rtype: bytes
        """
        return _ONE_SHORT.pack(0 << 15 | 1 << 14 | self._command)
