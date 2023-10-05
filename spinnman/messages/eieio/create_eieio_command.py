# Copyright (c) 2015 The University of Manchester
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from spinnman.messages.eieio.command_messages import (
    PaddingRequest, EventStopRequest, StopRequests, StartRequests,
    SpinnakerRequestBuffers, HostSendSequencedData, SpinnakerRequestReadData,
    HostDataRead, EIEIOCommandHeader, EIEIOCommandMessage,
    NotificationProtocolDatabaseLocation)
from spinnman.constants import EIEIO_COMMAND_IDS


def read_eieio_command_message(data, offset):
    """
    Reads the content of an EIEIO command message and returns an object
    identifying the command which was contained in the packet, including
    any parameter, if required by the command.

    :param bytes data: data received from the network as a byte-string
    :param int offset: offset at which the parsing operation should start
    :return: an object which inherits from EIEIOCommandMessage which contains
        parsed data received from the network
    :rtype: EIEIOCommandMessage
    """
    command_header = EIEIOCommandHeader.from_bytestring(data, offset)
    command_number = command_header.command

    if command_number == EIEIO_COMMAND_IDS.DATABASE.value:
        return NotificationProtocolDatabaseLocation.from_bytestring(
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
