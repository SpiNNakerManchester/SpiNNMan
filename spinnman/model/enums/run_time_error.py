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
    #: No error
    NONE = 0
    #: Branch through zero
    RESET = 1
    #: Undefined instruction
    UNDEF = 2
    #: Undefined SVC or no handler
    SVC = 3
    #: Prefetch abort
    PABT = 4
    #: Data abort
    DABT = 5
    #: Unhandled IRQ
    IRQ = 6
    #: Unhandled FIQ
    FIQ = 7
    #: Unconfigured VIC vector
    VIC = 8
    #: Generic user abort
    ABORT = 9
    #: "malloc" failure
    MALLOC = 10
    #: Divide by zero
    DIVBY0 = 11
    #: Event startup failure
    EVENT = 12
    #: Fatal SW error
    SWERR = 13
    #: Failed to allocate IO buffer
    IOBUF = 14
    #: Bad event enable
    ENABLE = 15
    #: Generic null pointer error
    NULL = 16
    #: Pkt startup failure
    PKT = 17
    #: Timer startup failure
    TIMER = 18
    #: API startup failure
    API = 19
    #: SW version conflict
    SARK_VERSRION_INCORRECT = 20

    def __new__(cls, value, doc=""):
        # pylint: disable=protected-access, unused-argument
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, value, doc=""):
        self._value_ = value
        self.__doc__ = doc
