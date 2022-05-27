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
from spinnman.exceptions import SpinnmanInvalidParameterException
from spinnman.messages.scp import SCPRequestHeader
from spinnman.messages.scp.abstract_messages import AbstractSCPRequest
from spinnman.messages.scp.enums import SCPCommand
from spinnman.messages.sdp import SDPFlag, SDPHeader
from spinnman.messages.scp.impl.check_ok_response import CheckOKResponse


_WAIT_FLAG = 0x1 << 18


class AppCopyRun(AbstractSCPRequest):
    """ An SCP request to copy an application and start it
    """
    __slots__ = ["__link"]

    def __init__(self, x, y, link, size, app_id, processors, wait=False):
        """
        :param int x:
            The x-coordinate of the chip to read from, between 0 and 255
        :param int y:
            The y-coordinate of the chip to read from, between 0 and 255
        :param int link: The ID of the link from which to copy
        :param int size: The number of bytes to read, must be divisible by 4
        :param int app_id: The app to associate the copied binary with
        :param list(int) processors: The processors to start on the chip
        :param bool wait: Whether to start in wait mode or not
        """
        # pylint: disable=too-many-arguments
        if size % 4 != 0:
            raise SpinnmanInvalidParameterException(
                "size", size, "The size must be a multiple of 4")

        processor_mask = 0
        if processors is not None:
            for processor in processors:
                processor_mask |= (1 << processor)

        processor_mask |= (app_id << 24)
        if wait:
            processor_mask |= _WAIT_FLAG
        self.__link = link

        super().__init__(
            SDPHeader(
                flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                destination_cpu=0, destination_chip_x=x,
                destination_chip_y=y),
            SCPRequestHeader(command=SCPCommand.CMD_APP_COPY_RUN),
            argument_1=link, argument_2=size, argument_3=processor_mask)

    def __repr__(self):
        return f"{super(AppCopyRun, self).__repr__()} (Link {self.__link})"

    @overrides(AbstractSCPRequest.get_scp_response)
    def get_scp_response(self):
        return CheckOKResponse(
            f"Application Copy Run (Link {self.__link})",
            SCPCommand.CMD_APP_COPY_RUN)
