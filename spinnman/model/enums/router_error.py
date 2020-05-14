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


class RouterError(Enum):
    """ Router error flags
    """
    #: Error packet detected (0x80000000)
    ERROR = (0x80000000, "Error packet detected")
    #: More than one error packet detected (0x40000000)
    OVERFLOW = (0x40000000, "More than one error packet detected")
    #: Parity Error (0x20000000)
    PARITY = (0x20000000, "Parity Error")
    #: Framing Error (0x10000000)
    FRAMING = (0x10000000, "Framing Error")
    #: Timestamp Error (0x08000000)
    TIMESTAMP = (0x08000000, "Timestamp Error")

    def __new__(cls, value, doc=""):
        # pylint: disable=protected-access, unused-argument
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, value, doc=""):
        self._value_ = value
        self.__doc__ = doc
