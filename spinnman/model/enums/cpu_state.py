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
    #: Dead core
    DEAD = 0
    #: Powered down
    POWERED_DOWN = 1
    #: Died with Run Time Error
    RUN_TIME_EXCEPTION = 2
    #: Watchdog expired
    WATCHDOG = 3
    #: Initialising (transient)
    INITIALISING = 4
    #: Ready to execute
    READY = 5
    #: Entered c_main
    C_MAIN = 6
    #: Running (API/Event)
    RUNNING = 7
    #: Waiting for sync 0
    SYNC0 = 8
    #: Waiting for sync 1
    SYNC1 = 9
    #: Paused in application
    PAUSED = 10
    #: Exited application
    FINISHED = 11
    #: Spare
    CPU_STATE_12 = 12
    #: Spare
    CPU_STATE_13 = 13
    #: Spare
    CPU_STATE_14 = 14
    #: Idle (SARK stub)
    IDLE = 15

    def __new__(cls, value, doc=""):
        # pylint: disable=protected-access, unused-argument
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, value, doc=""):
        self._value_ = value
        self.__doc__ = doc
