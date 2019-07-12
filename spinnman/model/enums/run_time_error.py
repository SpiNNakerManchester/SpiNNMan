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


class RunTimeError(Enum):
    """ SARK Run time errors
    """
    NONE = 0
    RESET = 1
    UNDEF = 2
    SVC = 3
    PABT = 4
    DABT = 5
    IRQ = 6
    FIQ = 7
    VIC = 8
    ABORT = 9
    MALLOC = 10
    DIVBY0 = 11
    EVENT = 12
    SWERR = 13
    IOBUF = 14
    ENABLE = 15
    NULL = 16
    PKT = 17
    TIMER = 18
    API = 19
    SARK_VERSRION_INCORRECT = 20

    def __new__(cls, value, doc=""):
        # pylint: disable=protected-access, unused-argument
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, value, doc=""):
        self._value_ = value
        self.__doc__ = doc
