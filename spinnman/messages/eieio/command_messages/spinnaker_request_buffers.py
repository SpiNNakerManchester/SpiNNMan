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

import struct
from .eieio_command_message import EIEIOCommandMessage
from .eieio_command_header import EIEIOCommandHeader
from spinnman.constants import EIEIO_COMMAND_IDS

_PATTERN_BBBxBBI = struct.Struct("<BBBxBBI")


class SpinnakerRequestBuffers(EIEIOCommandMessage):
    """ Message used in the context of the buffering input mechanism which is\
        sent by the SpiNNaker system to the host computer to ask for more data\
        to inject during the simulation
    """
    __slots__ = [
        "_region_id",
        "_sequence_no",
        "_space_available",
        "_p", "_x", "_y"]

    def __init__(self, x, y, p, region_id, sequence_no, space_available):
        # pylint: disable=too-many-arguments
        super(SpinnakerRequestBuffers, self).__init__(EIEIOCommandHeader(
            EIEIO_COMMAND_IDS.SPINNAKER_REQUEST_BUFFERS))
        self._x = x
        self._y = y
        self._p = p
        self._region_id = region_id
        self._sequence_no = sequence_no
        self._space_available = space_available

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def p(self):
        return self._p

    @property
    def region_id(self):
        return self._region_id

    @property
    def sequence_no(self):
        return self._sequence_no

    @property
    def space_available(self):
        return self._space_available

    @staticmethod
    def get_min_packet_length():
        return 12

    @staticmethod
    def from_bytestring(command_header, data, offset):  # @UnusedVariable
        y, x, processor, region_id, sequence_no, space = \
            _PATTERN_BBBxBBI.unpack_from(data, offset)
        p = (processor >> 3) & 0x1F
        return SpinnakerRequestBuffers(
            x, y, p, region_id & 0xF, sequence_no, space)

    @property
    def bytestring(self):
        return (super(SpinnakerRequestBuffers, self).bytestring +
                _PATTERN_BBBxBBI.pack(
                    self._y, self._x, self._p << 3, self._region_id,
                    self._sequence_no, self._space_available))
