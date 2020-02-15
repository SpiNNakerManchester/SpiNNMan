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
from spinn_utilities.overrides import overrides
from spinnman.messages.scp import SCPRequestHeader
from spinnman.messages.scp.abstract_messages import (
    AbstractSCPRequest, AbstractSCPResponse)
from spinnman.messages.scp.enums import (
    AllocFree, SCPCommand, SCPResult)
from spinnman.messages.sdp import SDPFlag, SDPHeader
from spinnman.exceptions import SpinnmanUnexpectedResponseCodeException

_ONE_WORD = struct.Struct("<I")


class RouterAlloc(AbstractSCPRequest):
    """ An SCP Request to allocate space for routing entries
    """
    __slots__ = []

    def __init__(self, x, y, app_id, n_entries):
        """
        :param x: \
            The x-coordinate of the chip to allocate on, between 0 and 255
        :type x: int
        :param y: \
            The y-coordinate of the chip to allocate on, between 0 and 255
        :type y: int
        :param app_id: The ID of the application, between 0 and 255
        :type app_id: int
        :param n_entries: The number of entries to allocate
        :type n_entries: int
        """
        super(RouterAlloc, self).__init__(
            SDPHeader(
                flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                destination_cpu=0, destination_chip_x=x,
                destination_chip_y=y),
            SCPRequestHeader(command=SCPCommand.CMD_ALLOC),
            argument_1=(
                (app_id << 8) |
                AllocFree.ALLOC_ROUTING.value),  # @UndefinedVariable
            argument_2=n_entries)

    @overrides(AbstractSCPRequest.get_scp_response)
    def get_scp_response(self):
        return _SCPRouterAllocResponse()


class _SCPRouterAllocResponse(AbstractSCPResponse):
    """ An SCP response to a request to allocate router entries
    """
    __slots__ = [
        "_base_address"]

    def __init__(self):
        """
        """
        super(_SCPRouterAllocResponse, self).__init__()
        self._base_address = None

    @overrides(AbstractSCPResponse.read_data_bytestring)
    def read_data_bytestring(self, data, offset):
        result = self.scp_response_header.result
        if result != SCPResult.RC_OK:
            raise SpinnmanUnexpectedResponseCodeException(
                "Router Allocation", "CMD_ALLOC", result.name)
        self._base_address = _ONE_WORD.unpack_from(data, offset)[0]

    @property
    def base_address(self):
        """ The base address allocated, or 0 if none

        :rtype: int
        """
        return self._base_address
