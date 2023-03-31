# Copyright (c) 2015 The University of Manchester
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


class DiagnosticFilterPacketType(Enum):
    """
    Packet type flags for the diagnostic filters.

    .. note::
        Only one has to match for the counter to be incremented.
    """
    #: Packet is multicast
    MULTICAST = (0, "Packet is multicast")
    #: Packet is point-to-point
    POINT_TO_POINT = (1, "Packet is point-to-point")
    #: Packet is nearest-neighbour
    NEAREST_NEIGHBOUR = (2, "Packet is nearest-neighbour")
    #: Packet is fixed-route
    FIXED_ROUTE = (3, "Packet is fixed-route")

    def __new__(cls, value, doc=""):
        # pylint: disable=protected-access, unused-argument
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, value, doc=""):
        self._value_ = value
        self.__doc__ = doc
