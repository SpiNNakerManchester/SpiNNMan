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
from spinnman.messages.sdp import SDPFlag, SDPHeader
from .check_ok_response import CheckOKResponse


class RouterClear(AbstractSCPRequest):
    """ A request to clear the router on a chip
    """
    __slots__ = []

    def __init__(self, x, y):
        """
        :param x: The x-coordinate of the chip, between 0 and 255; \
            this is not checked due to speed restrictions
        :type x: int
        :param y: The y-coordinate of the chip, between 0 and 255; \
            this is not checked due to speed restrictions
        :type y: int
        :raise spinnman.exceptions.SpinnmanInvalidParameterException:\
            * If x is out of range
            * If y is out of range
        """
        super(RouterClear, self).__init__(
            SDPHeader(
                flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                destination_cpu=0, destination_chip_x=x,
                destination_chip_y=y),
            SCPRequestHeader(command=SCPCommand.CMD_RTR))

    @overrides(AbstractSCPRequest.get_scp_response)
    def get_scp_response(self):
        return CheckOKResponse("RouterClear", "CMD_RTR")
