# Copyright (c) 2014 The University of Manchester
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

from enum import Enum


class SDP_PORTS(Enum):
    """
    SDP port handling output buffering data streaming.
    """

    #: Command port for the buffered in functionality.
    INPUT_BUFFERING_SDP_PORT = 1
    #: Command port for the buffered out functionality.
    OUTPUT_BUFFERING_SDP_PORT = 2
    #: Command port for resetting runtime, etc.
    #: See :py:class:`SDP_RUNNING_MESSAGE_CODES`
    RUNNING_COMMAND_SDP_PORT = 3
    #: Extra monitor core reinjection control protocol.
    #: See :py:class:`ReinjectorSCPCommands`
    EXTRA_MONITOR_CORE_REINJECTION = 4
    #: Extra monitor core outbound data transfer protocol
    EXTRA_MONITOR_CORE_DATA_SPEED_UP = 5
    #: Extra monitor core inbound data transfer protocol
    #: See :py:class:`SpeedupInSCPCommands`
    EXTRA_MONITOR_CORE_DATA_IN_SPEED_UP = 6
    #: Extra monitor core data copy
    EXTRA_MONITOR_CORE_COPY_DATA_IN = 7
