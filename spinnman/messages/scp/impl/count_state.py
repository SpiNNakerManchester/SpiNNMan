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
    """
    An SCP Request to get a count of the cores in a particular state.
    """
    __slots__ = []

    def __init__(self, app_id, state):
        """
        :param int app_id: The ID of the application, between 0 and 255
        :param CPUState state: The state to count
        """
        super().__init__(
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
