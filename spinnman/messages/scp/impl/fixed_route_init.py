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
from spinnman.messages.scp.abstract_messages import AbstractSCPRequest
from spinnman.messages.scp.enums import SCPCommand
from .check_ok_response import CheckOKResponse
from spinnman.messages.sdp import SDPHeader, SDPFlag


class FixedRouteInit(AbstractSCPRequest):
    __slots__ = []

    def __init__(self, x, y, entry, app_id):
        """ Sets a fixed route entry

        :param x: The x-coordinate of the chip, between 0 and 255,\
            this is not checked due to speed restrictions
        :type x: int
        :param y: The y-coordinate of the chip, between 0 and 255,\
            this is not checked due to speed restrictions
        :type y: int
        :param entry: the fixed route entry converted for writing
        :param app_id: The ID of the application with which to associate the\
            routes.  If not specified, defaults to 0.
        :type app_id: int
        :raise spinnman.exceptions.SpinnmanInvalidParameterException:\
            * If x is out of range
            * If y is out of range
        """

        super(FixedRouteInit, self).__init__(
            SDPHeader(
                flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                destination_cpu=0, destination_chip_x=x,
                destination_chip_y=y),
            SCPRequestHeader(command=SCPCommand.CMD_RTR),
            argument_1=(app_id << 8) | 3, argument_2=entry)

    @overrides(AbstractSCPRequest.get_scp_response)
    def get_scp_response(self):
        return CheckOKResponse("RouterInit", "CMD_RTR")
