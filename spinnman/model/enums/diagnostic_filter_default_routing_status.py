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


class DiagnosticFilterDefaultRoutingStatus(Enum):
    """ Default routing flags for the diagnostic filters.
        Note that only one has to match for the counter to be incremented
    """
    #: Packet is to be default routed
    DEFAULT_ROUTED = (0, "Packet is to be default routed")
    #: Packet is not to be default routed
    NON_DEFAULT_ROUTED = (1, "Packet is not to be default routed")

    def __new__(cls, value, doc=""):
        # pylint: disable=protected-access, unused-argument
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, value, doc=""):
        self._value_ = value
        self.__doc__ = doc
