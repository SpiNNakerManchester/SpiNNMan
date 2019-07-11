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

_NNP_FORWARD_RETRY = (1 << 31) | (0x3f << 8) | 0x18
_NNP_FLOOD_FILL_START = 6


class FloodFillStart(AbstractSCPRequest):
    """ A request to start a flood fill of data
    """
    __slots__ = []

    def __init__(self, nearest_neighbour_id, n_blocks, x=None, y=None):
        """
        :param nearest_neighbour_id: The ID of the packet, between 0 and 127
        :type nearest_neighbour_id: int
        :param n_blocks: The number of blocks of data that will be sent,\
            between 0 and 255
        :type n_blocks: int
        :param x: The x-coordinate of the chip to load the data on to. If not\
            specified, the data will be loaded on to all chips
        :type x: int
        :param y: The y-coordinate of the chip to load the data on to. If not\
            specified, the data will be loaded on to all chips
        :type y: int
        """
        key = ((_NNP_FLOOD_FILL_START << 24) | (nearest_neighbour_id << 16) |
               (n_blocks << 8))
        data = 0xFFFF
        if x is not None and y is not None:
            m = ((y & 3) * 4) + (x & 3)
            data = (((x & 0xfc) << 24) + ((y & 0xfc) << 16) +
                    (3 << 16) + (1 << m))

        super(FloodFillStart, self).__init__(
            SDPHeader(
                flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                destination_cpu=0,
                destination_chip_x=self.DEFAULT_DEST_X_COORD,
                destination_chip_y=self.DEFAULT_DEST_Y_COORD),
            SCPRequestHeader(command=SCPCommand.CMD_NNP),
            argument_1=key, argument_2=data, argument_3=_NNP_FORWARD_RETRY)

    @overrides(AbstractSCPRequest.get_scp_response)
    def get_scp_response(self):
        return CheckOKResponse("Flood Fill", "CMD_NNP:NNP_FFS")
