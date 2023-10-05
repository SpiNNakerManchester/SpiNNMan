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


class DiagnosticFilterDestination(Enum):
    """
    Destination flags for the diagnostic filters.

    .. note::
        Only one has to match for the counter to be incremented.
    """
    #: Destination is to dump the packet
    DUMP = (0, "Destination is to dump the packet")
    #: Destination is a local core (but not the monitor core)
    LOCAL = (1, "Destination is a local core (but not the monitor core)")
    #: Destination is the local monitor core
    LOCAL_MONITOR = (2, "Destination is the local monitor core")
    #: Destination is link 0
    LINK_0 = (3, "Destination is link 0")
    #: Destination is link 1
    LINK_1 = (4, "Destination is link 1")
    #: Destination is link 2
    LINK_2 = (5, "Destination is link 2")
    #: Destination is link 3
    LINK_3 = (6, "Destination is link 3")
    #: Destination is link 4
    LINK_4 = (7, "Destination is link 4")
    #: Destination is link 5
    LINK_5 = (8, "Destination is link 5")

    def __new__(cls, value, doc=""):
        # pylint: disable=protected-access, unused-argument
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, value, doc=""):
        self._value_ = value
        self.__doc__ = doc
