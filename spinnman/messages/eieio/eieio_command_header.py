from spinnman import exceptions
import math

class EIEIOCommandHeader(object):

    def __init__(self, command):
        self._command = command
        self._key_prefix = 0
        self._format = 1

    @property
    def command(self):
        return self._command

    @staticmethod
    def create_header_from_reader(byte_reader):
        """ Read an eieio command header from a byte_reader

        :param byte_reader: The reader to read the data from
        :type byte_reader:\
                    :py:class:`spinnman.data.abstract_byte_reader.AbstractByteReader`
        :return: a eieio command header
        :rtype: :py:class:`spinnman.data.eieio.eieio_header.EIEIOHeader`
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    reading from the reader
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If there\
                    are too few bytes to read the header
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If there\
                    is an error setting any of the values
        """
        first_part_of_command = byte_reader.read_byte()
        last_byte = byte_reader.read_byte()

        if ((last_byte >> 6) & 1) != 1 or ((last_byte >> 7) & 1) != 0:
            raise exceptions.SpinnmanInvalidPacketException(
                "this cannot be a eieio command header as the format does not"
                " match the correct format", "")

        last_part_of_command = ((last_byte & (math.pow(2, 6) - 1)) << 8)
        command = first_part_of_command + last_part_of_command

        return EIEIOCommandHeader(command)

    def write_command_header(self, writer):
        """ method which converts a python eieio command header into a byte array

        :param writer: the writer for byte arrays
        :type writer: implementation of spinnman.data.abstract_data_writer.AbstractDataWriter
        :return: None
        """
        header_short = self._key_prefix << 15 + self._format << 14 + self.command
        writer.write_short(header_short)