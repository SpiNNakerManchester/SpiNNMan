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

import struct
from spinnman.exceptions import SpinnmanInvalidParameterException
from spinnman.messages.eieio import EIEIOType
from .abstract_data_element import AbstractDataElement

_TWO_SHORTS = struct.Struct("<HH")
_TWO_WORDS = struct.Struct("<II")


class KeyPayloadDataElement(AbstractDataElement):
    """ A data element that contains a key and a payload
    """
    __slots__ = [
        "_key",
        "_payload",
        "_payload_is_timestamp"]

    def __init__(self, key, payload, payload_is_timestamp=False):
        self._key = key
        self._payload = payload
        self._payload_is_timestamp = payload_is_timestamp

    @property
    def key(self):
        return self._key

    @property
    def payload(self):
        return self._payload

    @property
    def payload_is_timestamp(self):
        return self._payload_is_timestamp

    def get_bytestring(self, eieio_type):
        if eieio_type.payload_bytes == 0:
            raise SpinnmanInvalidParameterException(
                "eieio_type", eieio_type,
                "The type specifies no payload, but this element has a "
                "payload")
        if eieio_type == EIEIOType.KEY_PAYLOAD_16_BIT:
            return _TWO_SHORTS.pack(self._key, self._payload)
        elif eieio_type == EIEIOType.KEY_PAYLOAD_32_BIT:
            return _TWO_WORDS.pack(self._key, self._payload)
        else:
            raise SpinnmanInvalidParameterException(
                "eieio_type", eieio_type, "Unknown type")

    def __str__(self):
        return "KeyPayloadDataElement:{}:{}".format(
            hex(self._key), hex(self._payload))

    def __repr__(self):
        return self.__str__()
