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

_NNP_FORWARD_RETRY = (0x3f << 8) | 0x1A
_NNP_FLOOD_FILL_END = 15
_WAIT_FLAG = 0x1 << 18


class FloodFillEnd(AbstractSCPRequest):
    """
    A request to start a flood fill of data.
    """
    __slots__ = []

    def __init__(
            self, nearest_neighbour_id, app_id=0, processors=None, wait=False):
        """

        :param int nearest_neighbour_id:
            The ID of the packet, between 0 and 127
        :param int app_id: The application ID to start using the data, between
            16 and 255.  If not specified, no application is started
        :param list(int) processors:
            A list of processors on which to start the application, each
            between 1 and 17. If not specified, no application is started.
        :param bool wait:
            True if the binary should go into a "wait" state before executing
        """
        processor_mask = 0
        if processors is not None:
            for processor in processors:
                processor_mask |= (1 << processor)

        key = (_NNP_FLOOD_FILL_END << 24) | nearest_neighbour_id
        data = (app_id << 24) | processor_mask
        if wait:
            data = data | _WAIT_FLAG

        super().__init__(
            SDPHeader(flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                      destination_cpu=0,
                      destination_chip_x=self.DEFAULT_DEST_X_COORD,
                      destination_chip_y=self.DEFAULT_DEST_Y_COORD),
            SCPRequestHeader(command=SCPCommand.CMD_NNP),
            argument_1=key, argument_2=data, argument_3=_NNP_FORWARD_RETRY)

    @overrides(AbstractSCPRequest.get_scp_response)
    def get_scp_response(self):
        return CheckOKResponse("Flood Fill", "CMD_NNP:NNP_FFS")
