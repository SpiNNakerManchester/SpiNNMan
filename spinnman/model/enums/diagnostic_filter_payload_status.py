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


class DiagnosticFilterPayloadStatus(Enum):
    """
    Payload flags for the diagnostic filters.

    .. note::
        Only one has to match for the counter to be incremented.
    """
    #: Packet has a payload
    WITH_PAYLOAD = (0, "Packet has a payload")
    #: Packet doesn't have a payload
    WITHOUT_PAYLOAD = (1, "Packet doesn't have a payload")

    def __new__(cls, value, doc=""):
        # pylint: disable=protected-access, unused-argument
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, value, doc=""):
        self._value_ = value
        self.__doc__ = doc
