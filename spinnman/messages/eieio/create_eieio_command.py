from spinnman.messages.eieio.command_messages \
    import PaddingRequest, EventStopRequest, StopRequests, StartRequests
from spinnman.messages.eieio.command_messages \
    import SpinnakerRequestBuffers, HostSendSequencedData
from spinnman.messages.eieio.command_messages \
    import SpinnakerRequestReadData, HostDataRead, EIEIOCommandHeader
from spinnman.messages.eieio.command_messages \
    import EIEIOCommandMessage, DatabaseConfirmation
from spinnman.constants import EIEIO_COMMAND_IDS


def read_eieio_command_message(data, offset):
    """ Reads the content of an EIEIO command message and returns an object\
        identifying the command which was contained in the packet, including\
        any parameter, if required by the command

    :param data: data received from the network as a bytestring
    :type data: str
    :param offset: offset at which the parsing operation should start
    :type offset: int
    :return: an object which inherits from EIEIOCommandMessage which contains\
            parsed data received from the network
    :rtype: \
            :py:class:`spinnman.messages.eieio.command_messages.eieio_command_message.EIEIOCommandMessage`
    """
    command_header = EIEIOCommandHeader.from_bytestring(data, offset)
    command_number = command_header.command

    if command_number == EIEIO_COMMAND_IDS.DATABASE_CONFIRMATION.value:
        return DatabaseConfirmation.from_bytestring(
            command_header, data, offset + 2)
    # Fill in buffer area with padding
    elif command_number == EIEIO_COMMAND_IDS.EVENT_PADDING.value:
        return PaddingRequest()
    # End of all buffers, stop execution
    elif command_number == EIEIO_COMMAND_IDS.EVENT_STOP.value:
        return EventStopRequest()
    # Stop complaining that there is sdram free space for buffers
    elif command_number == EIEIO_COMMAND_IDS.STOP_SENDING_REQUESTS.value:
        return StopRequests()
    # Start complaining that there is sdram free space for buffers
    elif command_number == EIEIO_COMMAND_IDS.START_SENDING_REQUESTS.value:
        return StartRequests()
    # Spinnaker requesting new buffers for spike source population
    elif command_number == EIEIO_COMMAND_IDS.SPINNAKER_REQUEST_BUFFERS.value:
        return SpinnakerRequestBuffers.from_bytestring(
            command_header, data, offset + 2)
    # Buffers being sent from host to SpiNNaker
    elif command_number == EIEIO_COMMAND_IDS.HOST_SEND_SEQUENCED_DATA.value:
        return HostSendSequencedData.from_bytestring(
            command_header, data, offset + 2)
    # Buffers available to be read from a buffered out vertex
    elif command_number == EIEIO_COMMAND_IDS.SPINNAKER_REQUEST_READ_DATA.value:
        return SpinnakerRequestReadData.from_bytestring(
            command_header, data, offset + 2)
    # Host confirming data being read form SpiNNaker memory
    elif command_number == EIEIO_COMMAND_IDS.HOST_DATA_READ.value:
        return HostDataRead.from_bytestring(
            command_header, data, offset + 2)
    return EIEIOCommandMessage(command_header, data, offset + 2)
