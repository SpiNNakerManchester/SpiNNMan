from spinnman.messages.eieio.abstract_messages import AbstractEIEIOMessage


class EIEIOCommandMessage(AbstractEIEIOMessage):
    """ An EIEIO command message
    """

    def __init__(self, eieio_command_header, data=None, offset=0):
        """

        :param eieio_command_header: The header of the message
        :type eieio_command_header:\
                    :py:class:`spinnman.messages.eieio.command_messages.eieio_command_header.EIEIOCommandHeader`
        :param data: Optional incoming data
        :type data: str
        :param offset: Offset into the data where valid data begins
        :type offset: int
        """
        AbstractEIEIOMessage.__init__(self)

        # The header
        self._eieio_command_header = eieio_command_header

        # The data
        self._data = data
        self._offset = offset

    @property
    def eieio_header(self):
        return self._eieio_command_header

    @property
    def data(self):
        return self._data

    @property
    def offset(self):
        return self._offset

    @staticmethod
    def from_bytestring(command_header, data, offset):
        return EIEIOCommandMessage(command_header, data, offset)

    @property
    def bytestring(self):
        return self._eieio_command_header.bytestring

    @staticmethod
    def get_min_packet_length():
        return 2

    def __str__(self):
        return "EIEIOCommandMessage:{}".format(self._eieio_command_header)

    def __repr__(self):
        return self.__str__()
