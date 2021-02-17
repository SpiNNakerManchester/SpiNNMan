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

import logging
from spinn_utilities.log import FormatAdapter
from spinn_utilities.overrides import overrides
from spinnman.messages.scp.abstract_messages import (
    AbstractSCPRequest, BMPRequest)
from spinnman.messages.scp.enums import SCPCommand
from spinnman.messages.scp import SCPRequestHeader
from .check_ok_response import CheckOKResponse

logger = FormatAdapter(logging.getLogger(__name__))


class SetPower(BMPRequest):
    """ An SCP request for the BMP to power on or power off a rack of boards
    """
    __slots__ = []

    def __init__(self, power_command, boards, delay=0.0, board_to_send_to=0):
        """
        .. note::
            There is currently a bug in the BMP that means some boards don't\
            respond to power commands not sent to BMP 0. Thus changing the\
            board_to_send_to parameter is not recommended!

        :param PowerCommand power_command: The power command being sent
        :param boards: The boards on the same backplane to power on or off
        :type boards: int or list(int)
        :param float delay:
            Number of seconds delay between power state changes of
            the different boards.
        :param int board_to_send_to:
            The optional board to send the command to if this is to be sent
            to a frame of boards.

            .. note::
                Leave this at the default because of hardware bugs.
        """

        if board_to_send_to != 0:
            logger.warning(
                "There is currently a bug in the BMP that means some boards"
                " don't respond to power commands not sent to BMP 0.  Thus "
                "changing the board_to_send_to is not recommended!")

        arg1 = (int(delay * 1000) << 16) | power_command.value
        arg2 = self.get_board_mask(boards)

        super().__init__(
            board_to_send_to,
            SCPRequestHeader(command=SCPCommand.CMD_BMP_POWER),
            argument_1=arg1, argument_2=arg2)

    @overrides(AbstractSCPRequest.get_scp_response)
    def get_scp_response(self):
        return CheckOKResponse("powering request", "CMD_BMP_POWER")
