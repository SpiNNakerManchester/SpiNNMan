# Copyright (c) 2015-2023 The University of Manchester
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from .eieio_command_message import EIEIOCommandMessage
from .eieio_command_header import EIEIOCommandHeader
from spinnman.constants import EIEIO_COMMAND_IDS


class NotificationProtocolStartResume(EIEIOCommandMessage):
    """ Packet which indicates that the toolchain has started or resumed.

    This message is not sent to SpiNNaker boards but rather to an auxiliary
    tool (e.g., data visualiser).
    """
    __slots__ = []

    def __init__(self):
        super().__init__(EIEIOCommandHeader(
            EIEIO_COMMAND_IDS.START_RESUME_NOTIFICATION))

    @staticmethod
    def from_bytestring(command_header, data, offset):
        return NotificationProtocolStartResume()
