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

from enum import Enum


class DiagnosticFilterPacketType(Enum):
    """ Packet type flags for the diagnostic filters.
        Note that only one has to match for the counter to be incremented
    """
    #: Packet is multicast
    MULTICAST = (0, "Packet is multicast")
    #: Packet is point-to-point
    POINT_TO_POINT = (1, "Packet is point-to-point")
    #: Packet is nearest-neighbour
    NEAREST_NEIGHBOUR = (2, "Packet is nearest-neighbour")
    #: Packet is fixed-route
    FIXED_ROUTE = (3, "Packet is fixed-route")

    def __new__(cls, value, doc=""):
        # pylint: disable=protected-access, unused-argument
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, value, doc=""):
        self._value_ = value
        self.__doc__ = doc
