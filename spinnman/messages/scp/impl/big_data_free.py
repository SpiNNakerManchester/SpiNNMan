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
from spinnman.messages.scp.abstract_messages import AbstractSCPRequest
from spinnman.messages.scp.enums import SCPCommand
from spinnman.messages.sdp import SDPFlag, SDPHeader
from spinnman.messages.scp import SCPRequestHeader
from .check_ok_response import CheckOKResponse
from spinnman.messages.scp.enums.big_data_command import BigDataCommand


class BigDataFree(AbstractSCPRequest):
    """ An SCP request to free big data
    """
    __slots__ = []

    def __init__(self, x, y):
        """
        :param x: The x-coordinate of the chip to send the command to
        :param y: The y-coordinate of the chip to send the command to
        """

        super(BigDataFree, self).__init__(
            SDPHeader(flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                      destination_cpu=0, destination_chip_x=x,
                      destination_chip_y=y),
            SCPRequestHeader(command=SCPCommand.CMD_BIG_DATA),
            argument_1=BigDataCommand.BIG_DATA_FREE.value)

    @overrides(AbstractSCPRequest.get_scp_response)
    def get_scp_response(self):
        return CheckOKResponse("Free Big Data", "CMD_BIG_DATA")
