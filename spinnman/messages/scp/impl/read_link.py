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

from spinn_utilities.overrides import overrides
from spinnman.messages.scp import SCPRequestHeader
from spinnman.messages.scp.abstract_messages import (
    AbstractSCPRequest, AbstractSCPResponse)
from spinnman.messages.scp.enums import SCPCommand, SCPResult
from spinnman.messages.sdp import SDPFlag, SDPHeader
from spinnman.exceptions import SpinnmanUnexpectedResponseCodeException


class ReadLink(AbstractSCPRequest):
    """ An SCP request to read a region of memory via a link on a chip
    """
    __slots__ = []

    def __init__(self, x, y, link, base_address, size, cpu=0):
        """
        :param x: The x-coordinate of the chip to read from, between 0 and 255
        :type x: int
        :param y: The y-coordinate of the chip to read from, between 0 and 255
        :type y: int
        :param cpu: The CPU core to use, normally 0 (or if a BMP, the board \
            slot number)
        :type cpu: int
        :param link: The ID of the link down which to send the query
        :type link: int
        :param base_address: The positive base address to start the read from
        :type base_address: int
        :param size: The number of bytes to read, between 1 and 256
        :type size: int
        """
        # pylint: disable=too-many-arguments
        super(ReadLink, self).__init__(
            SDPHeader(
                flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                destination_cpu=cpu, destination_chip_x=x,
                destination_chip_y=y),
            SCPRequestHeader(command=SCPCommand.CMD_LINK_READ),
            argument_1=base_address, argument_2=size, argument_3=link)

    @overrides(AbstractSCPRequest.get_scp_response)
    def get_scp_response(self):
        return _SCPReadLinkResponse()


class _SCPReadLinkResponse(AbstractSCPResponse):
    """ An SCP response to a request to read a region of memory via a link on\
        a chip
    """
    __slots__ = [
        "_data",
        "_length",
        "_offset"]

    def __init__(self):
        super(_SCPReadLinkResponse, self).__init__()
        self._data = None
        self._offset = None
        self._length = None

    @overrides(AbstractSCPResponse.read_data_bytestring)
    def read_data_bytestring(self, data, offset):
        result = self.scp_response_header.result
        if result != SCPResult.RC_OK:
            raise SpinnmanUnexpectedResponseCodeException(
                "ReadLink", "CMD_READ_LINK", result.name)
        self._data = data
        self._offset = offset
        self._length = len(data) - offset

    @property
    def data(self):
        """ The data read

        :rtype: bytearray
        """
        return self._data

    @property
    def offset(self):
        """ The offset where the valid data starts

        :rtype: int
        """
        return self._offset

    @property
    def length(self):
        """ The length of the valid data

        :rtype: int
        """
        return self._length
