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
from spinnman.messages.scp.abstract_messages import (
    AbstractSCPRequest, BMPRequest)
from spinnman.messages.scp import SCPRequestHeader
from spinnman.messages.scp.enums import SCPCommand
from .get_version_response import GetVersionResponse


class BMPGetVersion(BMPRequest):
    """ An SCP request to read the version of software running on a core
    """

    def __init__(self, board):
        """
        :param board: The board to get the version from
        :type board: int
        :raise spinnman.exceptions.SpinnmanInvalidParameterException:
            * If the chip coordinates are out of range
            * If the processor is out of range
        """
        super(BMPGetVersion, self).__init__(
            board, SCPRequestHeader(command=SCPCommand.CMD_VER))

    @overrides(AbstractSCPRequest.get_scp_response)
    def get_scp_response(self):
        return GetVersionResponse()
