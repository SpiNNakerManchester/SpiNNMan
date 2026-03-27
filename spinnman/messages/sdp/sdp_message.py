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
from typing import Optional
from .sdp_header import SDPHeader


class SDPMessage(object):
    """
    Wraps up an SDP message with a header and optional data.
    """
    __slots__ = (
        "_data",
        "_offset",
        "_sdp_header")

    def __init__(self, sdp_header: SDPHeader,
                 data: Optional[bytes] = None, offset: int = 0):
        """
        :param sdp_header: The header of the message
        :param data: The data of the SDP packet, or `None` if no data
        :param offset: The offset where the valid data starts
        """
        self._sdp_header = sdp_header
        self._data = data
        self._offset = offset

    @property
    def bytestring(self) -> bytes:
        """ The byte-string of the message. """
        if self._data is not None:
            return self._sdp_header.bytestring + self._data[self._offset:]
        return self._sdp_header.bytestring

    @staticmethod
    def from_bytestring(data: bytes, offset: int) -> 'SDPMessage':
        """
        :param data:
        :param offset:
        :returns: The message from the byte-string.
        """
        sdp_header = SDPHeader.from_bytestring(data, offset)
        return SDPMessage(sdp_header, data, offset + 8)

    @property
    def sdp_header(self) -> SDPHeader:
        """ The header of the packet. """
        return self._sdp_header

    @property
    def data(self) -> Optional[bytes]:
        """ The data in the packet. """
        return self._data

    @property
    def offset(self) -> int:
        """ The offset where the valid data starts. """
        return self._offset
