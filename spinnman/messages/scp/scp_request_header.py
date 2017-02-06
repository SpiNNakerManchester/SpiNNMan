import struct


class SCPRequestHeader(object):
    """ Represents the header of an SCP Request
        Each optional parameter in the constructor can be set to a value other\
        than None once, after which it is immutable.  It is an error to set a\
        parameter that is not currently None.
    """

    def __init__(self, command, sequence=0):
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
        self._sequence = sequence

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
        self._sequence = sequence

    @property
    def bytestring(self):
        """ The header as a bytestring

        :return: The header as a bytestring
        :rtype: str
        """
        return struct.pack("<2H", self._command.value, self._sequence)
