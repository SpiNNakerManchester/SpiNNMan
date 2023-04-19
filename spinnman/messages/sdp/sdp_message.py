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

from .sdp_header import SDPHeader


class SDPMessage(object):
    """
    Wraps up an SDP message with a header and optional data.
    """
    __slots__ = [
        "_data",
        "_offset",
        "_sdp_header"]

    def __init__(self, sdp_header, data=None, offset=0):
        """
        :param SDPHeader sdp_header: The header of the message
        :param data: The data of the SDP packet, or `None` if no data
        :type data: bytes or bytearray or None
        :param int offset: The offset where the valid data starts
        """
        self._sdp_header = sdp_header
        self._data = data
        self._offset = offset

    @property
    def bytestring(self):
        """
        The byte-string of the message.

        :rtype: bytes
        """
        if self._data is not None:
            return self._sdp_header.bytestring + self._data[self._offset:]
        return self._sdp_header.bytestring

    @staticmethod
    def from_bytestring(data, offset):
        """
        :param bytes data:
        :param int offset:
        :rtype: SDPMessage
        """
        sdp_header = SDPHeader.from_bytestring(data, offset)
        return SDPMessage(sdp_header, data, offset + 8)

    @property
    def sdp_header(self):
        """
        The header of the packet.

        :rtype: SDPHeader
        """
        return self._sdp_header

    @property
    def data(self):
        """
        The data in the packet.

        :rtype: bytes or bytearray or None
        """
        return self._data

    @property
    def offset(self):
        """
        The offset where the valid data starts.

        :rtype: int
        """
        return self._offset
