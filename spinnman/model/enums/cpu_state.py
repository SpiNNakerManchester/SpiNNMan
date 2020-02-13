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


class CPUState(Enum):
    """ SARK CPU States
    """
    DEAD = 0
    POWERED_DOWN = 1
    RUN_TIME_EXCEPTION = 2
    WATCHDOG = 3
    INITIALISING = 4
    READY = 5
    C_MAIN = 6
    RUNNING = 7
    SYNC0 = 8
    SYNC1 = 9
    PAUSED = 10
    FINISHED = 11
    CPU_STATE_12 = 12
    CPU_STATE_13 = 13
    CPU_STATE_14 = 14
    IDLE = 15

    def __new__(cls, value, doc=""):
        # pylint: disable=protected-access, unused-argument
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, value, doc=""):
        self._value_ = value
        self.__doc__ = doc
