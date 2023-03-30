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

import struct
from spinnman.exceptions import SpinnmanInvalidParameterException
from spinnman.messages.eieio import EIEIOType
from .abstract_data_element import AbstractDataElement

_TWO_SHORTS = struct.Struct("<HH")
_TWO_WORDS = struct.Struct("<II")


class KeyPayloadDataElement(AbstractDataElement):
    """
    A data element that contains a key and a payload.
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
        return f"KeyPayloadDataElement:0x{self._key:x}:0x{self._payload:x}"

    def __repr__(self):
        return self.__str__()
