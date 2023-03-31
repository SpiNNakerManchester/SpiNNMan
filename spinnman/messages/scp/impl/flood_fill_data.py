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

_NNP_FORWARD_RETRY = (0x3f << 24) | (0x1E << 16)
_NNP_FLOOD_FILL_START = 6


class FloodFillData(AbstractSCPRequest):
    """
    A request to start a flood fill of data.
    """
    __slots__ = [
        "_data_to_write",
        "_offset",
        "_size"]

    def __init__(self, nearest_neighbour_id, block_no, base_address, data,
                 offset=0, length=None):
        """
        :param int nearest_neighbour_id:
            The ID of the packet, between 0 and 127
        :param int block_no: Which block this block is, between 0 and 255
        :param int base_address:
            The base address where the data is to be loaded
        :param bytes data:
            The data to load, between 4 and 256 bytes and the size must be
            divisible by 4
        """
        # pylint: disable=too-many-arguments
        self._size = length
        self._offset = offset
        self._data_to_write = data
        if length is None:
            self._size = len(data)

        argument_1 = _NNP_FORWARD_RETRY | nearest_neighbour_id
        argument_2 = (block_no << 16) | (((self._size // 4) - 1) << 8)

        super().__init__(
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
        datastring = super().bytestring
        data = self._data_to_write[self._offset:self._offset + self._size]
        return datastring + bytes(data)

    @overrides(AbstractSCPRequest.get_scp_response)
    def get_scp_response(self):
        return CheckOKResponse("Flood Fill", "CMD_NNP:NNP_FFS")
