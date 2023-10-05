# Copyright (c) 2017 The University of Manchester
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


class RouterError(Enum):
    """
    Router error flags.
    """
    #: Error packet detected (0x80000000)
    ERROR = (0x80000000, "Error packet detected")
    #: More than one error packet detected (0x40000000)
    OVERFLOW = (0x40000000, "More than one error packet detected")
    #: Parity Error (0x20000000)
    PARITY = (0x20000000, "Parity Error")
    #: Framing Error (0x10000000)
    FRAMING = (0x10000000, "Framing Error")
    #: Timestamp Error (0x08000000)
    TIMESTAMP = (0x08000000, "Timestamp Error")

    def __new__(cls, value, doc=""):
        # pylint: disable=protected-access, unused-argument
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, value, doc=""):
        self._value_ = value
        self.__doc__ = doc
