from spinnman.exceptions import SpinnmanInvalidParameterException
from spinnman.exceptions import SpinnmanIOException


class SCPRequestHeader(object):
    """ Represents the header of an SCP Request
        Each optional parameter in the constructor can be set to a value other\
        than None once, after which it is immutable.  It is an error to set a\
        parameter that is not currently None.
    """

    def __init__(self, command, sequence=None):
        """

        :param command: The SCP command
        :type command: :py:class:`spinnman.messages.scp.scp_command.SCPCommand`
        :param sequence: The number of the SCP packet in order of all packets\
                    sent or received, between 0 and 65535
        :type sequence: int
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If one\
                    of the parameters is incorrect
        """
        self._command = command
        self._sequence = None

        self.sequence = sequence

    @property
    def command(self):
        """ The command of the SCP packet

        :return: The command
        :rtype: :py:class:`spinnman.messages.scp.scp_command.SCPCommand`
        """
        return self._command

    @property
    def sequence(self):
        """ The sequence number of the SCP packet

        :return: The sequence number of the packet, between 0 and 65535
        :rtype: int
        """
        return self._sequence

    @sequence.setter
    def sequence(self, sequence):
        """ Set the sequence number of the SCP packet

        :param sequence: The sequence number to set, between 0 and 65535
        :type sequence: int
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If the\
                    sequence is out of range, or if it has already been set
        """
        if self._sequence is not None:
            raise SpinnmanInvalidParameterException(
                "sequence", str(sequence),
                "The sequence has already been set")
        if sequence is not None and (sequence < 0 or sequence > 65535):
            raise SpinnmanInvalidParameterException(
                "sequence", str(sequence),
                "The sequence must be between 0 and 65535")
        self._sequence = sequence

    def write_scp_request_header(self, byte_writer):
        """ Write the SCP header to a byte_writer

        :param byte_writer: The writer to write the data to
        :type byte_writer:\
                    :py:class:`spinnman.data.abstract_byte_writer.AbstractByteWriter`
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    writing to the writer
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If any\
                    of the parameter values have not been set
        """
        if self._command is None:
            raise SpinnmanInvalidParameterException(
                "scp_header.command", str(None), "No value has been assigned")
        if self._sequence is None:
            raise SpinnmanInvalidParameterException(
                "scp_header.sequence", str(None), "No value has been assigned")

        try:
            byte_writer.write_short(self._command.value)
            byte_writer.write_short(self._sequence)
        except IOError as exception:
            raise SpinnmanIOException(str(exception))
