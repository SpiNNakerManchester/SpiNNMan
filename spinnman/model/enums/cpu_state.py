# Copyright (c) 2014 The University of Manchester
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from enum import Enum


class CPUState(Enum):
    """
    SARK CPU States.
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
