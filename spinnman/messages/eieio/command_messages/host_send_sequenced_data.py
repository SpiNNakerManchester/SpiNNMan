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

import struct
from .eieio_command_message import EIEIOCommandMessage
from .eieio_command_header import EIEIOCommandHeader
from spinnman.constants import EIEIO_COMMAND_IDS
from spinnman.messages.eieio.create_eieio_data import read_eieio_data_message

_PATTERN_BB = struct.Struct("<BB")


class HostSendSequencedData(EIEIOCommandMessage):
    """
    Packet sent from the host to the SpiNNaker system in the context of
    buffering input mechanism to identify packet which needs to be stored
    in memory for future use.
    """
    __slots__ = [
        "_eieio_data_message",
        "_region_id",
        "_sequence_no"]

    def __init__(self, region_id, sequence_no, eieio_data_message):
        super().__init__(EIEIOCommandHeader(
            EIEIO_COMMAND_IDS.HOST_SEND_SEQUENCED_DATA))
        self._region_id = region_id
        self._sequence_no = sequence_no
        self._eieio_data_message = eieio_data_message

    @property
    def region_id(self):
        return self._region_id

    @property
    def sequence_no(self):
        return self._sequence_no

    @property
    def eieio_data_message(self):
        return self._eieio_data_message

    @staticmethod
    def get_min_packet_length():
        return 4

    @staticmethod
    def from_bytestring(command_header, data, offset):  # @UnusedVariable
        region_id, sequence_no = _PATTERN_BB.unpack_from(data, offset)
        eieio_data_message = read_eieio_data_message(data, offset)
        return HostSendSequencedData(
            region_id, sequence_no, eieio_data_message)

    @property
    def bytestring(self):
        return (super().bytestring +
                _PATTERN_BB.pack(self._region_id, self._sequence_no) +
                self._eieio_data_message.bytestring)
