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

from spinn_utilities.abstract_base import AbstractBase, abstractmethod
from spinnman.messages.sdp import SDPHeader
from spinnman.messages.scp import SCPResponseHeader

# The offset of the header from the start of a received packet
# (8 bytes of SDP header)
_SCP_HEADER_OFFSET = 8

# The offset of the data from the start of a received packet
# (8 bytes of SDP header + 4 bytes of SCP header)
_SCP_DATA_OFFSET = 12


class AbstractSCPResponse(object, metaclass=AbstractBase):
    """ Represents an abstract SCP Response.
    """
    __slots__ = [
        "_scp_response_header",
        "_sdp_header"]

    def __init__(self):
        self._sdp_header = None
        self._scp_response_header = None

    def read_bytestring(self, data, offset):
        """ Reads a packet from a bytestring of data

        :param bytes data: The bytestring to be read
        :param int offset:
            The offset in the data from which the response should be read
        """
        self._sdp_header = SDPHeader.from_bytestring(data, offset)
        self._scp_response_header = SCPResponseHeader.from_bytestring(
            data, _SCP_HEADER_OFFSET + offset)
        self.read_data_bytestring(data, _SCP_DATA_OFFSET + offset)

    @abstractmethod
    def read_data_bytestring(self, data, offset):
        """ Reads the remainder of the data following the header

        :param bytes data: The bytestring to read from
        :param int offset: The offset into the data after the headers
        """

    @property
    def sdp_header(self):
        """ The SDP header from the response

        :rtype: SDPHeader
        """
        return self._sdp_header

    @property
    def scp_response_header(self):
        """ The SCP header from the response

        :rtype: SCPResponseHeader
        """
        return self._scp_response_header
