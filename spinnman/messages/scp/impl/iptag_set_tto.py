# Copyright (c) 2015 The University of Manchester
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

_IPTAG_TTO = (4 << 16)


class IPTagSetTTO(AbstractSCPRequest):
    """
    An SCP request to set the transient timeout for future SCP requests.
    """
    __slots__ = []

    def __init__(self, x, y, tag_timeout):
        """
        :param int x: The x-coordinate of the chip to run on, between 0 and 255
        :param int y: The y-coordinate of the chip to run on, between 0 and 255
        :param IPTAG_TIME_OUT_WAIT_TIMES tag_timeout: The timeout value
        """
        super().__init__(
            SDPHeader(flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                      destination_cpu=0, destination_chip_x=x,
                      destination_chip_y=y),
            SCPRequestHeader(command=SCPCommand.CMD_IPTAG),
            argument_1=_IPTAG_TTO, argument_2=tag_timeout.value)

    @overrides(AbstractSCPRequest.get_scp_response)
    def get_scp_response(self):
        return IPTagGetInfoResponse()
