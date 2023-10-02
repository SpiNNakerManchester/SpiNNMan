# Copyright (c) 2016 The University of Manchester
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
from .get_chip_info_response import GetChipInfoResponse


class GetChipInfo(AbstractSCPRequest):
    """
    An SCP request to read the chip information from a core.
    """
    __slots__ = []

    def __init__(self, x, y, with_size=False):
        """
        :param int x:
            The x-coordinate of the chip to read from, between 0 and 255
        :param int y:
            The y-coordinate of the chip to read from, between 0 and 255
        :param bool with_size:
            Whether the size should be included in the response
        """
        # Bits 0-4 + bit 6 = all information except size
        argument_1 = 0x5F
        if with_size:

            # Bits 0-6 = all information including size
            argument_1 = 0x7F

        super().__init__(
            SDPHeader(
                flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                destination_cpu=0, destination_chip_x=x,
                destination_chip_y=y),
            SCPRequestHeader(command=SCPCommand.CMD_INFO),
            argument_1=argument_1)

    @overrides(AbstractSCPRequest.get_scp_response)
    def get_scp_response(self):
        return GetChipInfoResponse()
