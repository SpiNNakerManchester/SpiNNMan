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
from spinn_machine import FixedRouteEntry
from spinnman.exceptions import SpinnmanUnexpectedResponseCodeException
from spinnman.messages.scp import SCPRequestHeader
from spinnman.messages.scp.abstract_messages import (
    AbstractSCPRequest, AbstractSCPResponse)
from spinnman.messages.scp.enums import SCPCommand, SCPResult
from spinnman.messages.sdp import SDPHeader, SDPFlag

_ONE_WORD = struct.Struct("<I")


class FixedRouteRead(AbstractSCPRequest):
    __slots__ = []

    def __init__(self, x, y, app_id):
        """ Sets a fixed route entry

        :param x: The x-coordinate of the chip, between 0 and 255,\
            this is not checked due to speed restrictions
        :type x: int
        :param y: The y-coordinate of the chip, between 0 and 255\
            this is not checked due to speed restrictions
        :type y: int
        :param app_id: The ID of the application with which to associate the\
            routes.  If not specified, defaults to 0.
        :type app_id: int
        :raise spinnman.exceptions.SpinnmanInvalidParameterException:\
            * If x is out of range
            * If y is out of range
        """
        super(FixedRouteRead, self).__init__(
            SDPHeader(
                flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                destination_cpu=0, destination_chip_x=x,
                destination_chip_y=y),
            SCPRequestHeader(command=SCPCommand.CMD_RTR),
            argument_1=(app_id << 8) | 3, argument_2=1 << 31)

    @overrides(AbstractSCPRequest.get_scp_response)
    def get_scp_response(self):
        return _FixedRouteResponse()


class _FixedRouteResponse(AbstractSCPResponse):
    """
    response for the fixed route read
    """
    __slots__ = [
        # the fixed route router entry
        "_route"]

    def __init__(self):
        super(_FixedRouteResponse, self).__init__()
        self._route = None

    @overrides(AbstractSCPResponse.read_data_bytestring)
    def read_data_bytestring(self, data, offset):
        result = self.scp_response_header.result
        if result != SCPResult.RC_OK:
            raise SpinnmanUnexpectedResponseCodeException(
                "Read Fixed Route entry", "CMD_RTR", result.name)

        self._route = _ONE_WORD.unpack_from(data, offset)[0]

    @property
    def route(self):
        processor_ids = list()
        for processor_id in range(0, 26):
            if self._route & (1 << (6 + processor_id)) != 0:
                processor_ids.append(processor_id)
        link_ids = list()
        for link_id in range(0, 6):
            if self._route & (1 << link_id) != 0:
                link_ids.append(link_id)
        return FixedRouteEntry(processor_ids, link_ids)
