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
from spinnman.messages.scp.abstract_messages import AbstractSCPRequest
from spinnman.messages.scp.enums import SCPCommand
from spinnman.messages.sdp import SDPFlag, SDPHeader
from spinnman.messages.scp import SCPRequestHeader
from .check_ok_response import CheckOKResponse

_WAIT_FLAG = 0x1 << 18


class ApplicationRun(AbstractSCPRequest):
    """ An SCP request to run an application loaded on a chip
    """
    __slots__ = []

    def __init__(self, app_id, x, y, processors, wait=False):
        """
        :param app_id: The ID of the application to run, between 16 and 255
        :type app_id: int
        :param x: The x-coordinate of the chip to run on, between 0 and 255
        :type x: int
        :param y: The y-coordinate of the chip to run on, between 0 and 255
        :type y: int
        :param processors: \
            The processors on the chip where the executable should be \
            started, between 1 and 17
        :type processors: list of int
        :param wait: \
            True if the processors should enter a "wait" state on starting
        :type wait: bool
        """
        # pylint: disable=too-many-arguments
        processor_mask = 0
        if processors is not None:
            for processor in processors:
                processor_mask |= (1 << processor)

        processor_mask |= (app_id << 24)
        if wait:
            processor_mask |= _WAIT_FLAG

        super(ApplicationRun, self).__init__(
            SDPHeader(flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                      destination_cpu=0, destination_chip_x=x,
                      destination_chip_y=y),
            SCPRequestHeader(command=SCPCommand.CMD_AR),
            argument_1=processor_mask)

    @overrides(AbstractSCPRequest.get_scp_response)
    def get_scp_response(self):
        return CheckOKResponse("Run Application", "CMD_AR")
