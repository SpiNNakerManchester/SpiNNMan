# Copyright (c) 2017 The University of Manchester
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
from .check_ok_response import CheckOKResponse
from spinnman.messages.sdp import SDPHeader, SDPFlag


class FixedRouteInit(AbstractSCPRequest):
    """
    Sets a fixed route entry.
    """
    __slots__ = []

    def __init__(self, x, y, entry, app_id):
        """
        :param int x: The x-coordinate of the chip, between 0 and 255,
            this is not checked due to speed restrictions
        :param int y: The y-coordinate of the chip, between 0 and 255,
            this is not checked due to speed restrictions
        :param int entry: the fixed route entry converted for writing
        :param int app_id:
            The ID of the application with which to associate the routes.
            If not specified, defaults to 0.
        :raise SpinnmanInvalidParameterException:
            * If x is out of range
            * If y is out of range
        """
        super().__init__(
            SDPHeader(
                flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                destination_cpu=0, destination_chip_x=x,
                destination_chip_y=y),
            SCPRequestHeader(command=SCPCommand.CMD_RTR),
            argument_1=(app_id << 8) | 3, argument_2=entry)

    @overrides(AbstractSCPRequest.get_scp_response)
    def get_scp_response(self):
        return CheckOKResponse("RouterInit", "CMD_RTR")
