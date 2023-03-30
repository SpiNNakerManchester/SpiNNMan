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


class SignalType(Enum):
    """
    The type of signal, determined by how it is transmitted.
    """
    MULTICAST = 0
    POINT_TO_POINT = 1
    NEAREST_NEIGHBOUR = 2


class Signal(Enum):
    """
    SCP Signals.
    """
    INITIALISE = (0, SignalType.NEAREST_NEIGHBOUR)
    POWER_DOWN = (1, SignalType.NEAREST_NEIGHBOUR)
    STOP = (2, SignalType.NEAREST_NEIGHBOUR)
    START = (3, SignalType.MULTICAST)
    SYNC0 = (4, SignalType.MULTICAST)
    SYNC1 = (5, SignalType.MULTICAST)
    PAUSE = (6, SignalType.MULTICAST)
    CONTINUE = (7, SignalType.MULTICAST)
    EXIT = (8, SignalType.MULTICAST)
    TIMER = (9, SignalType.MULTICAST)
    USER_0 = (10, SignalType.MULTICAST)
    USER_1 = (11, SignalType.MULTICAST)
    USER_2 = (12, SignalType.MULTICAST)
    USER_3 = (13, SignalType.MULTICAST)

    def __new__(cls, value, signal_type, doc=""):
        # pylint: disable=protected-access, unused-argument
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, value, signal_type, doc=""):
        """
        :param int value: The value used for the signal
        :param SignalType signal_type: The "type" of the signal
        """
        self._value_ = value
        self._signal_type = signal_type
        self.__doc__ = doc

    @property
    def signal_type(self):
        return self._signal_type
