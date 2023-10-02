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


class SDPFlag(Enum):
    """
    SDPFlag for the message.
    """
    REPLY_NOT_EXPECTED = (0x07, "Indicates that a reply is not expected")
    REPLY_EXPECTED = (0x87, "Indicates that a reply is expected")
    REPLY_NOT_EXPECTED_NO_P2P = (
        0x07 | 0x20,
        "Indicates that a reply is not expected and packet should not be P2P "
        "routed")
    REPLY_EXPECTED_NO_P2P = (
        0x87 | 0x20,
        "Indicates that a reply is expected and packet should not be P2P "
        "routed")

    def __new__(cls, value, doc=""):
        # pylint: disable=protected-access, unused-argument
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, value, doc=""):
        self._value_ = value
        self.__doc__ = doc
