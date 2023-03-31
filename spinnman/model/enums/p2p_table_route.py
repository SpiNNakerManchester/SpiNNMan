# Copyright (c) 2016 The University of Manchester
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


class P2PTableRoute(Enum):
    """
    P2P Routing table routes.
    """
    EAST = 0b000
    NORTH_EAST = 0b001
    NORTH = 0b010
    WEST = 0b011
    SOUTH_WEST = 0b100
    SOUTH = 0b101
    #: No route to this chip
    NONE = (0b110, "No route to this chip")
    #: Route to the monitor on the current chip
    MONITOR = (0b111, "Route to the monitor on the current chip")

    def __new__(cls, value, doc=""):
        # pylint: disable=protected-access, unused-argument
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, value, doc=""):
        self._value_ = value
        self.__doc__ = doc
