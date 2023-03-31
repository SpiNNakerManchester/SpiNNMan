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


class EIEIOType(Enum):
    """
    Possible types of EIEIO packets.
    """
    KEY_16_BIT = (0, 2, 0, "Indicates that data is keys which are 16 bits")
    KEY_PAYLOAD_16_BIT = (
        1, 2, 2, "Indicates that data is keys and payloads of 16 bits")
    KEY_32_BIT = (2, 4, 0, "Indicates that data is keys of 32 bits")
    KEY_PAYLOAD_32_BIT = (
        3, 4, 4, "Indicates that data is keys and payloads of 32 bits")

    def __new__(cls, value, key_bytes, payload_bytes, doc=""):
        # pylint: disable=protected-access, unused-argument
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, value, key_bytes, payload_bytes, doc=""):
        self._value_ = value
        self._key_bytes = key_bytes
        self._payload_bytes = payload_bytes
        self.__doc__ = doc

    @property
    def key_bytes(self):
        """
        The number of bytes used by each key element.

        :rtype: int
        """
        return self._key_bytes

    @property
    def payload_bytes(self):
        """
        The number of bytes used by each payload element.

        :rtype: int
        """
        return self._payload_bytes

    @property
    def max_value(self):
        """
        The maximum value of the key or payload (if there is a payload).

        :rtype: int
        """
        return (1 << (self._key_bytes * 8)) - 1
