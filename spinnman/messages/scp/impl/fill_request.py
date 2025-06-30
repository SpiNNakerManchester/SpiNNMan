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
from spinnman.messages.sdp import SDPFlag, SDPHeader
from spinnman.messages.scp import SCPRequestHeader
from spinnman.messages.scp.enums import SCPCommand
from spinnman.messages.scp.abstract_messages import AbstractSCPRequest
from .check_ok_response import CheckOKResponse


class FillRequest(AbstractSCPRequest[CheckOKResponse]):
    """
    An SCP request to fill a region of memory on a chip with repeated data
    """
    __slots__ = ()

    def __init__(
            self, x: int, y: int, base_address: int, data: int, size: int):
        """
        :param x:
            The x-coordinate of the chip to read from, between 0 and 255
        :param y:
            The y-coordinate of the chip to read from, between 0 and 255
        :param base_address:
            The positive base address to start the fill from
        :param data: The data to fill in the space with
        :param size: The number of bytes to fill in
        """
        super().__init__(
            SDPHeader(
                flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                destination_cpu=0, destination_chip_x=x,
                destination_chip_y=y),
            SCPRequestHeader(command=SCPCommand.CMD_FILL),
            argument_1=base_address, argument_2=data,
            argument_3=size)

    @overrides(AbstractSCPRequest.get_scp_response)
    def get_scp_response(self) -> CheckOKResponse:
        return CheckOKResponse("Fill", SCPCommand.CMD_FILL)
