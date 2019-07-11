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
from .get_chip_info_response import GetChipInfoResponse


class GetChipInfo(AbstractSCPRequest):
    """ An SCP request to read the chip information from a core
    """
    __slots__ = []

    def __init__(self, x, y, with_size=False):
        """
        :param x: The x-coordinate of the chip to read from, between 0 and 255
        :type x: int
        :param y: The y-coordinate of the chip to read from, between 0 and 255
        :type y: int
        :param with_size: Whether the size should be included in the response
        :type with_size: bool
        """
        # Bits 0-4 + bit 6 = all information except size
        argument_1 = 0x5F
        if with_size:

            # Bits 0-6 = all information including size
            argument_1 = 0x7F

        super(GetChipInfo, self).__init__(
            SDPHeader(
                flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                destination_cpu=0, destination_chip_x=x,
                destination_chip_y=y),
            SCPRequestHeader(command=SCPCommand.CMD_INFO),
            argument_1=argument_1)

    @overrides(AbstractSCPRequest.get_scp_response)
    def get_scp_response(self):
        return GetChipInfoResponse()
