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
from .iptag_get_info_response import IPTagGetInfoResponse

_IPTAG_INFO = 4
_IPTAG_MAX = 255


class IPTagGetInfo(AbstractSCPRequest[IPTagGetInfoResponse]):
    """
    An SCP Request information about IP tags.
    """
    __slots__ = ()

    def __init__(self, x: int, y: int):
        """
        :param x: The x-coordinate of a chip, between 0 and 255
        :param y: The y-coordinate of a chip, between 0 and 255
        """
        super().__init__(
            SDPHeader(
                flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                destination_cpu=0, destination_chip_x=x,
                destination_chip_y=y),
            SCPRequestHeader(command=SCPCommand.CMD_IPTAG),
            argument_1=(_IPTAG_INFO << 16),
            argument_2=_IPTAG_MAX)

    @overrides(AbstractSCPRequest.get_scp_response)
    def get_scp_response(self) -> IPTagGetInfoResponse:
        return IPTagGetInfoResponse()
