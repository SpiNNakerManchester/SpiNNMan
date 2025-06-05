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
from spinnman.model.enums import CPUState
from .count_state_response import CountStateResponse


class CountState(AbstractSCPRequest[CountStateResponse]):
    """
    An SCP Request to get a count of the cores in a particular state.
    """
    __slots__ = ()

    def __init__(self, x: int, y: int, app_id: int, state: CPUState):
        """
        :param app_id: The ID of the application, between 0 and 255
        :param state: The state to count
        """
        super().__init__(
            SDPHeader(
                flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                destination_cpu=0,
                destination_chip_x=x,
                destination_chip_y=y),
            SCPRequestHeader(command=SCPCommand.CMD_COUNT),
            argument_1=app_id,
            argument_2=state.value)

    @overrides(AbstractSCPRequest.get_scp_response)
    def get_scp_response(self) -> CountStateResponse:
        return CountStateResponse()
