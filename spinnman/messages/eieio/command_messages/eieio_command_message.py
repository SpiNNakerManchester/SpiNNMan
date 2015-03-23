from spinnman.messages.eieio.command_messages.eieio_command_header\
    import EIEIOCommandHeader
from spinnman.messages.eieio.abstract_messages.abstract_eieio_message\
    import AbstractEIEIOMessage

from spinnman import constants

from spinnman.messages.eieio.command_messages.padding_request\
    import PaddingRequest
from spinnman.messages.eieio.command_messages.event_stop_request\
    import EventStopRequest
from spinnman.messages.eieio.command_messages.stop_requests\
    import StopRequests
from spinnman.messages.eieio.command_messages.start_requests\
    import StartRequests
from spinnman.messages.eieio.command_messages.spinnaker_request_buffers\
    import SpinnakerRequestBuffers
from spinnman.messages.eieio.command_messages.host_send_sequenced_data\
    import HostSendSequencedData
from spinnman.messages.eieio.command_messages.spinnaker_request_read_data\
    import SpinnakerRequestReadData
from spinnman.messages.eieio.command_messages.host_data_read\
    import HostDataRead


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
    def read_eieio_message(byte_reader):
        command_header = EIEIOCommandHeader.read_eieio_header(byte_reader)
        command_number = command_header.command

        # Fill in buffer area with padding
        if (command_number ==
                constants.EIEIO_COMMAND_IDS.EVENT_PADDING.value):
            return PaddingRequest.read_eieio_command_message(
                command_header, byte_reader)

        # End of all buffers, stop execution
        elif (command_number ==
                constants.EIEIO_COMMAND_IDS.EVENT_STOP.value):
            return EventStopRequest.read_eieio_command_message(
                command_header, byte_reader)

        # Stop complaining that there is sdram free space for buffers
        elif (command_number ==
                constants.EIEIO_COMMAND_IDS.STOP_SENDING_REQUESTS.value):
            return StopRequests.read_eieio_command_message(
                command_header, byte_reader)

        # Start complaining that there is sdram free space for buffers
        elif (command_number ==
                constants.EIEIO_COMMAND_IDS.START_SENDING_REQUESTS.value):
            return StartRequests.read_eieio_command_message(
                command_header, byte_reader)

        # Spinnaker requesting new buffers for spike source population
        elif (command_number ==
                constants.EIEIO_COMMAND_IDS.SPINNAKER_REQUEST_BUFFERS.value):
            return SpinnakerRequestBuffers.read_eieio_command_message(
                command_header, byte_reader)

        # Buffers being sent from host to SpiNNaker
        elif (command_number ==
                constants.EIEIO_COMMAND_IDS.HOST_SEND_SEQUENCED_DATA.value):
            return HostSendSequencedData.read_eieio_command_message(
                command_header, byte_reader)

        # Buffers available to be read from a buffered out vertex
        elif (command_number ==
                constants.EIEIO_COMMAND_IDS.SPINNAKER_REQUEST_READ_DATA.value):
            return SpinnakerRequestReadData.read_eieio_command_message(
                command_header, byte_reader)

        # Host confirming data being read form SpiNNaker memory
        elif (command_number ==
                constants.EIEIO_COMMAND_IDS.HOST_DATA_READ.value):
            return HostDataRead.read_eieio_command_message(
                command_header, byte_reader)
        return EIEIOCommandMessage(command_header, byte_reader)

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
