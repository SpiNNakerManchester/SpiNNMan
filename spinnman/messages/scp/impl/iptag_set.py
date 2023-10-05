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

_IPTAG_SET = 1


class IPTagSet(AbstractSCPRequest):
    """
    An SCP Request to set an IP Tag.
    """
    __slots__ = []

    def __init__(self, x, y, host, port, tag, strip, use_sender=False):
        """
        :param int x: The x-coordinate of a chip, between 0 and 255
        :param int y: The y-coordinate of a chip, between 0 and 255
        :param host: The host address, as an array of 4 bytes
        :type host: bytearray or list(int)
        :param int port: The port, between 0 and 65535
        :param int tag: The tag, between 0 and 7
        :param bool strip: if the SDP header should be striped from the packet
        :param bool use_sender:
            if the sender IP address and port should be used
        """
        # pylint: disable=too-many-arguments
        strip_value = int(bool(strip))
        sender_value = int(bool(use_sender))
        super().__init__(
            SDPHeader(
                flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                destination_cpu=0, destination_chip_x=x,
                destination_chip_y=y),
            SCPRequestHeader(command=SCPCommand.CMD_IPTAG),
            argument_1=(strip_value << 28) | (sender_value << 30) |
                       (_IPTAG_SET << 16) | tag,
            argument_2=port,
            argument_3=((host[3] << 24) | (host[2] << 16) |
                        (host[1] << 8) | host[0]))

    @overrides(AbstractSCPRequest.get_scp_response)
    def get_scp_response(self):
        return CheckOKResponse("Set IP Tag", "CMD_IPTAG")
