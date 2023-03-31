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
from spinnman.messages.scp.abstract_messages import (
    AbstractSCPRequest, BMPRequest)
from spinnman.messages.scp import SCPRequestHeader
from spinnman.messages.scp.enums import SCPCommand
from .get_version_response import GetVersionResponse


class BMPGetVersion(BMPRequest):
    """
    An SCP request to read the version of software running on a core.
    """

    def __init__(self, board):
        """
        :param int board: The board to get the version from
        :raise SpinnmanInvalidParameterException:
            * If the chip coordinates are out of range
            * If the processor is out of range
        """
        super().__init__(
            board, SCPRequestHeader(command=SCPCommand.CMD_VER))

    @overrides(AbstractSCPRequest.get_scp_response)
    def get_scp_response(self):
        return GetVersionResponse()
