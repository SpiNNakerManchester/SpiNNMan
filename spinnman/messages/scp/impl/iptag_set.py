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

_IPTAG_SET = 1


class IPTagSet(AbstractSCPRequest):
    """ An SCP Request to set an IP Tag
    """
    __slots__ = []

    def __init__(self, x, y, host, port, tag, strip, use_sender=False):
        """
        :param x: The x-coordinate of a chip, between 0 and 255
        :type x: int
        :param y: The y-coordinate of a chip, between 0 and 255
        :type y: int
        :param host: The host address, as an array of 4 bytes
        :type host: bytearray
        :param port: The port, between 0 and 65535
        :type port: int
        :param tag: The tag, between 0 and 7
        :type tag: int
        :param strip: if the SDP header should be striped from the packet.
        :type strip: bool
        :param use_sender: if the sender ip address and port should be used
        :type: bool
        """
        # pylint: disable=too-many-arguments
        strip_value = int(bool(strip))
        sender_value = int(bool(use_sender))
        super(IPTagSet, self).__init__(
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
