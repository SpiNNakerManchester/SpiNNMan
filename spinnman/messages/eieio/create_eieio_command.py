# Copyright (c) 2017-2019 The University of Manchester
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from spinnman.messages.eieio.command_messages import (
    PaddingRequest, EventStopRequest, StopRequests, StartRequests,
    SpinnakerRequestBuffers, HostSendSequencedData, SpinnakerRequestReadData,
    HostDataRead, EIEIOCommandHeader, EIEIOCommandMessage,
    DatabaseConfirmation)
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
        :py:class:`spinnman.messages.eieio.command_messages.EIEIOCommandMessage`
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
    # Stop complaining that there is SDRAM free space for buffers
    elif command_number == EIEIO_COMMAND_IDS.STOP_SENDING_REQUESTS.value:
        return StopRequests()
    # Start complaining that there is SDRAM free space for buffers
    elif command_number == EIEIO_COMMAND_IDS.START_SENDING_REQUESTS.value:
        return StartRequests()
    # SpiNNaker requesting new buffers for spike source population
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
