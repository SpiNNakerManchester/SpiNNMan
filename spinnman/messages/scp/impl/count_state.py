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
from .count_state_response import CountStateResponse

_ALL_CORE_MASK = 0xFFFF
_COUNT_OPERATION = 1
_COUNT_MODE = 2
_COUNT_SIGNAL_TYPE = 1
_APP_MASK = 0xFF


def _get_data(app_id, state):
    data = (_APP_MASK << 8) | app_id
    data += (_COUNT_OPERATION << 22) | (_COUNT_MODE << 20)
    data += state.value << 16
    return data


class CountState(AbstractSCPRequest):
    """ An SCP Request to get a count of the cores in a particular state
    """
    __slots__ = []

    def __init__(self, app_id, state):
        """

        :param app_id: The ID of the application, between 0 and 255
        :type app_id: int
        :param state: The state to count
        :type state: :py:class:`spinnman.model.cpu_state.CPUState`
        """
        super(CountState, self).__init__(
            SDPHeader(
                flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                destination_cpu=0,
                destination_chip_x=self.DEFAULT_DEST_X_COORD,
                destination_chip_y=self.DEFAULT_DEST_Y_COORD),
            SCPRequestHeader(command=SCPCommand.CMD_SIG),
            argument_1=_COUNT_SIGNAL_TYPE,
            argument_2=_get_data(app_id, state),
            argument_3=_ALL_CORE_MASK)

    @overrides(AbstractSCPRequest.get_scp_response)
    def get_scp_response(self):
        return CountStateResponse()
