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


class EIEIOType(Enum):
    """ Possible types of EIEIO packets
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
        """ The number of bytes used by each key element

        :rtype: int
        """
        return self._key_bytes

    @property
    def payload_bytes(self):
        """ The number of bytes used by each payload element

        :rtype: int
        """
        return self._payload_bytes

    @property
    def max_value(self):
        """ The maximum value of the key or payload (if there is a payload)

        :rtype: int
        """
        return (1 << (self._key_bytes * 8)) - 1
