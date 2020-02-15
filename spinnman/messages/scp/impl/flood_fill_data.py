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

from __future__ import division
from spinn_utilities.overrides import overrides
from spinnman.messages.scp import SCPRequestHeader
from spinnman.messages.scp.abstract_messages import AbstractSCPRequest
from spinnman.messages.scp.enums import SCPCommand
from spinnman.messages.sdp import SDPFlag, SDPHeader
from .check_ok_response import CheckOKResponse

_NNP_FORWARD_RETRY = (0x3f << 24) | (0x1A << 16)
_NNP_FLOOD_FILL_START = 6


class FloodFillData(AbstractSCPRequest):
    """ A request to start a flood fill of data
    """
    __slots__ = [
        "_data_to_write",
        "_offset",
        "_size"]

    def __init__(self, nearest_neighbour_id, block_no, base_address, data,
                 offset=0, length=None):
        """
        :param nearest_neighbour_id: The ID of the packet, between 0 and 127
        :type nearest_neighbour_id: int
        :param block_no: Which block this block is, between 0 and 255
        :type block_no: int
        :param base_address: The base address where the data is to be loaded
        :type base_address: int
        :param data: The data to load, between 4 and 256 bytes and the size\
            must be divisible by 4
        :type data: bytearray
        """
        # pylint: disable=too-many-arguments
        self._size = length
        self._offset = offset
        self._data_to_write = data
        if length is None:
            self._size = len(data)

        argument_1 = _NNP_FORWARD_RETRY | nearest_neighbour_id
        argument_2 = (block_no << 16) | (((self._size // 4) - 1) << 8)

        super(FloodFillData, self).__init__(
            SDPHeader(
                flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                destination_cpu=0,
                destination_chip_x=self.DEFAULT_DEST_X_COORD,
                destination_chip_y=self.DEFAULT_DEST_Y_COORD),
            SCPRequestHeader(command=SCPCommand.CMD_FFD),
            argument_1=argument_1, argument_2=argument_2,
            argument_3=base_address, data=None)

    @property
    def bytestring(self):
        datastring = super(FloodFillData, self).bytestring
        data = self._data_to_write[self._offset:self._offset + self._size]
        return datastring + bytes(data)

    @overrides(AbstractSCPRequest.get_scp_response)
    def get_scp_response(self):
        return CheckOKResponse("Flood Fill", "CMD_NNP:NNP_FFS")
