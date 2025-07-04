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
from spinn_utilities.overrides import overrides
from spinnman.constants import EIEIO_COMMAND_IDS
from .eieio_command_message import EIEIOCommandMessage
from .eieio_command_header import EIEIOCommandHeader

_PATTERN_BBBxBBI = struct.Struct("<BBBxBBI")


class SpinnakerRequestBuffers(EIEIOCommandMessage):
    """
    Message used in the context of the buffering input mechanism which is
    sent by the SpiNNaker system to the host computer to ask for more data
    to inject during the simulation.
    """
    __slots__ = (
        "_region_id",
        "_sequence_no",
        "_space_available",
        "_p", "_x", "_y")

    def __init__(
            self, x: int, y: int, p: int, region_id: int, sequence_no: int,
            space_available: int):
        """

        :param x:
        :param y:
        :param p:
        :param region_id:
        :param sequence_no:
        :param space_available:
        """
        super().__init__(EIEIOCommandHeader(
            EIEIO_COMMAND_IDS.SPINNAKER_REQUEST_BUFFERS))
        self._x = x
        self._y = y
        self._p = p
        self._region_id = region_id
        self._sequence_no = sequence_no
        self._space_available = space_available

    @property
    def x(self) -> int:
        """ Gets the x value passed into the init """
        return self._x

    @property
    def y(self) -> int:
        """ Gets the y value passed into the init """
        return self._y

    @property
    def p(self) -> int:
        """ Gets the p value passed into the init """
        return self._p

    @property
    def region_id(self) -> int:
        """ Gets the region_id value passed into the init """
        return self._region_id

    @property
    def sequence_no(self) -> int:
        """ Gets the sequence_no value passed into the init """
        return self._sequence_no

    @property
    def space_available(self) -> int:
        """ Gets the space_available value passed into the init """
        return self._space_available

    @staticmethod
    @overrides(EIEIOCommandMessage.get_min_packet_length)
    def get_min_packet_length() -> int:
        return 12

    @staticmethod
    @overrides(EIEIOCommandMessage.from_bytestring)
    def from_bytestring(command_header: EIEIOCommandHeader, data: bytes,
                        offset: int) -> "SpinnakerRequestBuffers":
        y, x, processor, region_id, sequence_no, space = \
            _PATTERN_BBBxBBI.unpack_from(data, offset)
        p = (processor >> 3) & 0x1F
        return SpinnakerRequestBuffers(
            x, y, p, region_id & 0xF, sequence_no, space)

    @property
    @overrides(EIEIOCommandMessage.bytestring)
    def bytestring(self) -> bytes:
        return (super().bytestring + _PATTERN_BBBxBBI.pack(
            self._y, self._x, self._p << 3, self._region_id,
            self._sequence_no, self._space_available))
