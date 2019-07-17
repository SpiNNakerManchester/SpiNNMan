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
from spinnman.messages.scp.enums import SCPCommand, Signal
from spinnman.messages.sdp import SDPFlag, SDPHeader
from .check_ok_response import CheckOKResponse

_APP_MASK = 0xFF


def _get_data(app_id, signal):
    data = (_APP_MASK << 8) | app_id
    data += signal.value << 16
    return data


class AppStop(AbstractSCPRequest):
    """ An SCP Request to stop an application
    """
    __slots__ = []

    def __init__(self, app_id):
        """
        :param app_id: The ID of the application, between 0 and 255
        :type app_id: int
        """
        super(AppStop, self).__init__(
            SDPHeader(
                flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                destination_cpu=0,
                destination_chip_x=self.DEFAULT_DEST_X_COORD,
                destination_chip_y=self.DEFAULT_DEST_Y_COORD),
            SCPRequestHeader(command=SCPCommand.CMD_NNP),
            argument_1=(0x3f << 16),
            argument_2=(5 << 28) | _get_data(app_id, Signal.STOP),
            argument_3=(1 << 31) + (0x3f << 8))

    @overrides(AbstractSCPRequest.get_scp_response)
    def get_scp_response(self):
        return CheckOKResponse("Send Stop", "CMD_NNP")
