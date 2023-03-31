# Copyright (c) 2014 The University of Manchester
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from spinn_utilities.overrides import overrides
from spinnman.messages.scp import SCPRequestHeader
from spinnman.messages.scp.abstract_messages import AbstractSCPRequest
from spinnman.messages.scp.enums import SCPCommand
from spinnman.messages.sdp import SDPFlag, SDPHeader
from .check_ok_response import CheckOKResponse

_NNP_FORWARD_RETRY = (1 << 31) | (0x3f << 8) | 0x1A
_NNP_FLOOD_FILL_START = 6


class FloodFillStart(AbstractSCPRequest):
    """
    A request to start a flood fill of data.
    """
    __slots__ = []

    def __init__(self, nearest_neighbour_id, n_blocks, x=None, y=None):
        """
        :param int nearest_neighbour_id:
            The ID of the packet, between 0 and 127
        :param int n_blocks:
            The number of blocks of data that will be sent, between 0 and 255
        :param int x: The x-coordinate of the chip to load the data on to. If
            not specified, the data will be loaded on to all chips
        :param int y: The y-coordinate of the chip to load the data on to. If
            not specified, the data will be loaded on to all chips
        """
        key = ((_NNP_FLOOD_FILL_START << 24) | (nearest_neighbour_id << 16) |
               (n_blocks << 8))
        data = 0xFFFF
        if x is not None and y is not None:
            m = ((y & 3) * 4) + (x & 3)
            data = (((x & 0xfc) << 24) + ((y & 0xfc) << 16) +
                    (3 << 16) + (1 << m))

        super().__init__(
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
