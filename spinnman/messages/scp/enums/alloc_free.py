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


class AllocFree(Enum):
    """ The SCP Allocation and Free codes
    """

    ALLOC_SDRAM = (0, "Allocate SDRAM")
    FREE_SDRAM_BY_POINTER = (1, "Free SDRAM using a Pointer")
    FREE_SDRAM_BY_APP_ID = (2, "Free SDRAM using am APP ID")
    ALLOC_ROUTING = (3, "Allocate Routing Entries")
    FREE_ROUTING_BY_POINTER = (4, "Free Routing Entries by Pointer")
    FREE_ROUTING_BY_APP_ID = (5, "Free Routing Entries by APP ID")

    def __new__(cls, value, doc=""):
        # pylint: disable=protected-access, unused-argument
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, value, doc=""):
        self._value_ = value
        self.__doc__ = doc
