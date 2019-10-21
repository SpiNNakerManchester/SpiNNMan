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


class DiagnosticFilterDestination(Enum):
    """ Destination flags for the diagnostic filters.
        Note that only one has to match for the counter to be incremented
    """
    DUMP = (0, "Destination is to dump the packet")
    LOCAL = (1, "Destination is a local core (but not the monitor core)")
    LOCAL_MONITOR = (2, "Destination is the local monitor core")
    LINK_0 = (3, "Destination is link 0")
    LINK_1 = (4, "Destination is link 1")
    LINK_2 = (5, "Destination is link 2")
    LINK_3 = (6, "Destination is link 3")
    LINK_4 = (7, "Destination is link 4")
    LINK_5 = (8, "Destination is link 5")

    def __new__(cls, value, doc=""):
        # pylint: disable=protected-access, unused-argument
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, value, doc=""):
        self._value_ = value
        self.__doc__ = doc
