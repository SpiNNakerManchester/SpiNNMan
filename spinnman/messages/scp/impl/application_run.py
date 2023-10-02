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
from spinnman.messages.scp.abstract_messages import AbstractSCPRequest
from spinnman.messages.scp.enums import SCPCommand
from spinnman.messages.sdp import SDPFlag, SDPHeader
from spinnman.messages.scp import SCPRequestHeader
from .check_ok_response import CheckOKResponse

_WAIT_FLAG = 0x1 << 18


class ApplicationRun(AbstractSCPRequest):
    """
    An SCP request to run an application loaded on a chip.
    """
    __slots__ = []

    def __init__(self, app_id, x, y, processors, wait=False):
        """
        :param int app_id: The ID of the application to run, between 16 and 255
        :param int x: The x-coordinate of the chip to run on, between 0 and 255
        :param int y: The y-coordinate of the chip to run on, between 0 and 255
        :param list(int) processors:
            The processors on the chip where the executable should be
            started, between 1 and 17
        :param bool wait:
            True if the processors should enter a "wait" state on starting
        """
        # pylint: disable=too-many-arguments
        processor_mask = 0
        if processors is not None:
            for processor in processors:
                processor_mask |= (1 << processor)

        processor_mask |= (app_id << 24)
        if wait:
            processor_mask |= _WAIT_FLAG

        super().__init__(
            SDPHeader(flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                      destination_cpu=0, destination_chip_x=x,
                      destination_chip_y=y),
            SCPRequestHeader(command=SCPCommand.CMD_AR),
            argument_1=processor_mask)

    @overrides(AbstractSCPRequest.get_scp_response)
    def get_scp_response(self):
        return CheckOKResponse("Run Application", "CMD_AR")
