from spinnman.messages.eieio.abstract_messages.abstract_eieio_message\
    import AbstractEIEIOMessage


class EIEIOCommandMessage(AbstractEIEIOMessage):
    """ An EIEIO command message
    """

    def __init__(self, eieio_command_header, data_reader=None):
        """

        :param eieio_command_header: The header of the message
        :type eieio_command_header:\
                    :py:class:`spinnman.messages.eieio.command_messages.eieio_command_header.EIEIOCommandHeader`
        :param data_reader: Optional reader of incoming data
        :type data_reader:\
                    :py:class:`spinnman.data.abstract_data_reader.AbstractDataReader`
        """
        AbstractEIEIOMessage.__init__(self)

        # The header
        self._eieio_command_header = eieio_command_header

        # The data reader
        self._data_reader = data_reader

    @property
    def eieio_header(self):
        return self._eieio_command_header

    @property
    def data(self):
        return self._data_reader.read_bytes()

    @staticmethod
    def read_eieio_command_message(command_header, byte_reader):
        return EIEIOCommandMessage(command_header, byte_reader)

    def write_eieio_message(self, writer):
        self._eieio_command_header.write_eieio_header(writer)

    @staticmethod
    def get_min_packet_length():
        return 2

    def __str__(self):
        return "EIEIOCommandMessage:{}".format(self._eieio_command_header)

    def __repr__(self):
        return self.__str__()
