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

from spinnman.constants import EIEIO_COMMAND_IDS
from .eieio_command_message import EIEIOCommandMessage
from .eieio_command_header import EIEIOCommandHeader


class PaddingRequest(EIEIOCommandMessage):
    """ Packet used to pad space in the buffering area, if needed
    """
    __slots__ = []

    def __init__(self):
        super(PaddingRequest, self).__init__(EIEIOCommandHeader(
            EIEIO_COMMAND_IDS.EVENT_PADDING))

    @staticmethod
    def get_min_packet_length():
        return 2
