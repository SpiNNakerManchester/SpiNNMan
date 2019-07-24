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
from spinnman.constants import address_length_dtype


class ReadMemory(AbstractSCPRequest):
    """ An SCP request to read a region of memory on a chip
    """
    __slots__ = []

    def __init__(self, x, y, base_address, size, cpu=0):
        """
        :param x: The x-coordinate of the chip to read from, between 0 and 255
        :type x: int
        :param y: The y-coordinate of the chip to read from, between 0 and 255
        :type y: int
        :param base_address: The positive base address to start the read from
        :type base_address: int
        :param size: The number of bytes to read, between 1 and 256
        :type size: int
        :raise spinnman.exceptions.SpinnmanInvalidParameterException:
            * If the chip coordinates are out of range
            * If the base address is not a positive number
            * If the size is out of range
        """
        # pylint: disable=too-many-arguments
        super(ReadMemory, self).__init__(
            SDPHeader(
                flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                destination_cpu=cpu, destination_chip_x=x,
                destination_chip_y=y),
            SCPRequestHeader(command=SCPCommand.CMD_READ),
            argument_1=base_address, argument_2=size,
            argument_3=address_length_dtype[
                (base_address % 4, size % 4)].value)

    @overrides(AbstractSCPRequest.get_scp_response)
    def get_scp_response(self):
        return _SCPReadMemoryResponse()


class _SCPReadMemoryResponse(AbstractSCPResponse):
    """ An SCP response to a request to read a region of memory on a chip
    """
    __slots__ = [
        "_data",
        "_length",
        "_offset"]

    def __init__(self):
        super(_SCPReadMemoryResponse, self).__init__()
        self._data = None
        self._length = None
        self._offset = None

    @overrides(AbstractSCPResponse.read_data_bytestring)
    def read_data_bytestring(self, data, offset):
        if self._scp_response_header.result != SCPResult.RC_OK:
            raise SpinnmanUnexpectedResponseCodeException(
                "Read", "CMD_READ", self._scp_response_header.result)
        self._data = data
        self._offset = offset
        self._length = len(data) - offset

    @property
    def data(self):
        """ The data read - note that the data starts at offset

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
