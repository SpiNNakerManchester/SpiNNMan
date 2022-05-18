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
from spinnman.exceptions import SpinnmanInvalidParameterException

_NNP_FLOOD_COPY = 3
_FWD_RTRY = (1 << 31) | 0x3F00


class FloodFillCopy(AbstractSCPRequest):
    """ A request to flood fill of data by copy from neighbouring chips
    """
    __slots__ = []

    def __init__(self, address, n_words):
        """
        :param int address: The address to copy from/to
        :param int n_words: The number of words to copy
        """
        if n_words > 0xFFFF:
            raise SpinnmanInvalidParameterException(
                "n_words", n_words, "Must be 0xFFFF words or less")
        key = (_NNP_FLOOD_COPY << 24) | (n_words << 8)
        data = address
        super().__init__(
            SDPHeader(
                flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                destination_cpu=0,
                destination_chip_x=self.DEFAULT_DEST_X_COORD,
                destination_chip_y=self.DEFAULT_DEST_Y_COORD),
            SCPRequestHeader(command=SCPCommand.CMD_NNP),
            argument_1=key, argument_2=data, argument_3=_FWD_RTRY)

    @overrides(AbstractSCPRequest.get_scp_response)
    def get_scp_response(self):
        return CheckOKResponse("Flood Copy", "CMD_NNP:NNP_FCPY")
