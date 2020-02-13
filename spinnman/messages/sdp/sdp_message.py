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

from .sdp_header import SDPHeader


class SDPMessage(object):
    """ Wraps up an SDP message with a header and optional data.
    """
    __slots__ = [
        "_data",
        "_offset",
        "_sdp_header"]

    def __init__(self, sdp_header, data=None, offset=0):
        """
        :param sdp_header: The header of the message
        :type sdp_header:\
            :py:class:`spinnman.messages.sdp.sdp_header.SDPHeader`
        :param data: The data of the SDP packet, or None if no data
        :type data: bytes or bytearray or None
        :param offset: The offset where the valid data starts
        :type offset: int
        :raise None: No known exceptions are thrown
        """

        self._sdp_header = sdp_header
        self._data = data
        self._offset = offset

    @property
    def bytestring(self):
        """ The bytestring of the message

        :return: The bytestring of the message
        :rtype: str
        """
        if self._data is not None:
            return self._sdp_header.bytestring + self._data[self._offset:]
        return self._sdp_header.bytestring

    @staticmethod
    def from_bytestring(data, offset):
        sdp_header = SDPHeader.from_bytestring(data, offset)
        return SDPMessage(sdp_header, data, offset + 8)

    @property
    def sdp_header(self):
        """ The header of the packet

        :return: An SDP header
        :rtype: :py:class:`spinnman.messages.sdp.sdp_header.SDPHeader`
        """
        return self._sdp_header

    @property
    def data(self):
        """ The data in the packet

        :rtype: bytes or bytearray or None
        """
        return self._data

    @property
    def offset(self):
        """ The offset where the valid data starts

        :rtype: int
        """
        return self._offset
