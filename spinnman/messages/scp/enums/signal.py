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


class SignalType(Enum):
    """ The type of signal, determined by how it is transmitted
    """
    MULTICAST = 0
    POINT_TO_POINT = 1
    NEAREST_NEIGHBOUR = 2


class Signal(Enum):
    """ SCP Signals
    """
    INITIALISE = (0, SignalType.NEAREST_NEIGHBOUR)
    POWER_DOWN = (1, SignalType.NEAREST_NEIGHBOUR)
    STOP = (2, SignalType.NEAREST_NEIGHBOUR)
    START = (3, SignalType.NEAREST_NEIGHBOUR)
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

        :param value: The value used for the signal
        :type value: int
        :param signal_type: The "type" of the signal
        :type signal_type: :py:class:`.SignalType`
        """
        self._value_ = value
        self._signal_type = signal_type
        self.__doc__ = doc

    @property
    def signal_type(self):
        return self._signal_type
