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

from .eieio_command_message import EIEIOCommandMessage
from .eieio_command_header import EIEIOCommandHeader
from spinnman.constants import EIEIO_COMMAND_IDS


class NotificationProtocolPauseStop(EIEIOCommandMessage):
    """ Packet which indicates that the toolchain has paused or stopped
    """
    __slots__ = []

    def __init__(self):
        super(NotificationProtocolPauseStop, self).__init__(EIEIOCommandHeader(
            EIEIO_COMMAND_IDS.STOP_PAUSE_NOTIFICATION))

    @property
    def bytestring(self):
        data = super(NotificationProtocolPauseStop, self).bytestring
        return data

    @staticmethod
    def from_bytestring(command_header, data, offset):
        return NotificationProtocolPauseStop()
