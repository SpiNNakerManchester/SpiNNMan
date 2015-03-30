from spinnman.exceptions import SpinnmanInvalidParameterException


class EIEIOCommandHeader(object):
    """ EIEIO header for command packets
    """

    def __init__(self, command):
        if command < 0 or command >= 16384:
            raise SpinnmanInvalidParameterException(
                "command", command,
                "parameter command is outside the allowed range (0 to 16383)")
        self._command = command

    @property
    def command(self):
        return self._command

    @staticmethod
    def read_eieio_header(byte_reader):
        """ Read an eieio command header from a byte_reader

        :param byte_reader: The reader to read the data from
        :type byte_reader:\
                    :py:class:`spinnman.data.abstract_byte_reader.AbstractByteReader`
        :return: an eieio command header
        :rtype:\
                    :py:class:`spinnman.messages.eieio.command_messages.eieio_command_header.EIEIOCommandHeader`
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    reading from the reader
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If there\
                    is an error setting any of the values
        """
        command_header = byte_reader.read_short()
        command = command_header & 0x3FFF

        return EIEIOCommandHeader(command)

    def write_eieio_header(self, writer):
        """ Write the command header to a writer

        :param writer: the writer to write the header to
        :type writer:\
                    :py:class:`spinnman.data.abstract_byte_writer.AbstractByteWriter`
        :return: None
        """
        writer.write_short(0 << 15 | 1 << 14 | self._command)
