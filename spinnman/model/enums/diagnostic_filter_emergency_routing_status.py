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


class DiagnosticFilterEmergencyRoutingStatus(Enum):
    """
    Emergency routing status flags for the diagnostic filters.

    .. note::
        Only one has to match for the counter to be incremented.
    """
    #: Packet is not emergency routed
    NORMAL = (0, "Packet is not emergency routed")
    #: Packet is in first hop of emergency route; packet should also have been
    #: sent here by normal routing
    FIRST_STAGE_COMBINED = (1, "Packet is in first hop of emergency route;"
                               " packet should also have been sent here by"
                               " normal routing")
    #: Packet is in first hop of emergency route; packet wouldn't have reached
    #: this router without emergency routing
    FIRST_STAGE = (2, "Packet is in first hop of emergency route; packet"
                      " wouldn't have reached this router without emergency"
                      " routing")
    #: Packet is in last hop of emergency route and should now return to normal
    #: routing
    SECOND_STAGE = (3, "Packet is in last hop of emergency route and should"
                       " now return to normal routing")

    def __new__(cls, value, doc=""):
        # pylint: disable=protected-access, unused-argument
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, value, doc=""):
        self._value_ = value
        self.__doc__ = doc
