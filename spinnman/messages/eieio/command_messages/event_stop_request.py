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

from spinnman.constants import EIEIO_COMMAND_IDS
from .eieio_command_message import EIEIOCommandMessage
from .eieio_command_header import EIEIOCommandHeader


class EventStopRequest(EIEIOCommandMessage):
    """
    Packet used for the buffering input technique which causes the parser
    of the input packet to terminate its execution.
    """
    __slots__ = ()

    def __init__(self) -> None:
        super().__init__(EIEIOCommandHeader(EIEIO_COMMAND_IDS.EVENT_STOP))
