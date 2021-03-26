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


class ReverseIPTagSet(AbstractSCPRequest):
    """ An SCP Request to set an IP Tag
    """
    __slots__ = []

    def __init__(self, x, y, destination_x, destination_y, destination_p, port,
                 tag, sdp_port):
        """
        :param int x: The x-coordinate of a chip, between 0 and 255
        :param int y: The y-coordinate of a chip, between 0 and 255
        :param int destination_x:
            The x-coordinate of the destination chip, between 0 and 255
        :param int destination_y:
            The y-coordinate of the destination chip, between 0 and 255
        :param int destination_p:
            The ID of the destination processor, between 0 and 17
        :param int port: The port, between 0 and 65535
        :param int tag: The tag, between 0 and 7
        """
        # pylint: disable=too-many-arguments
        strip_value = 1
        reverse_value = 1

        arg1 = ((reverse_value << 29) | (strip_value << 28) |
                (_IPTAG_SET << 16) | (sdp_port << 13) | (destination_p << 8) |
                tag)
        arg2 = ((destination_x << 24) | (destination_y << 16) | port)

        super().__init__(
            SDPHeader(
                flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                destination_cpu=0, destination_chip_x=x,
                destination_chip_y=y),
            SCPRequestHeader(command=SCPCommand.CMD_IPTAG),
            argument_1=arg1,
            argument_2=arg2,
            argument_3=0)

    @overrides(AbstractSCPRequest.get_scp_response)
    def get_scp_response(self):
        return CheckOKResponse("Set Reverse IP Tag", "CMD_IPTAG")
