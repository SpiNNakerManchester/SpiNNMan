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

_ONE_SHORT = struct.Struct("<H")
_ONE_WORD = struct.Struct("<I")


class KeyDataElement(AbstractDataElement):
    """
    A data element that contains just a key.
    """
    __slots__ = [
        "_key"]

    def __init__(self, key):
        self._key = key

    @property
    def key(self):
        return self._key

    def get_bytestring(self, eieio_type):
        if eieio_type.payload_bytes != 0:
            raise SpinnmanInvalidParameterException(
                "eieio_type", eieio_type,
                "The type specifies a payload, but this element has no"
                " payload")
        if eieio_type == EIEIOType.KEY_16_BIT:
            return _ONE_SHORT.pack(self._key)
        elif eieio_type == EIEIOType.KEY_32_BIT:
            return _ONE_WORD.pack(self._key)
        else:
            raise SpinnmanInvalidParameterException(
                "eieio_type", eieio_type, "Unknown type")

    def __str__(self):
        return f"KeyDataElement:0x{self._key:x}"

    def __repr__(self):
        return self.__str__()
