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
    """
    An SCP Request to stop an application.
    """
    __slots__ = []

    def __init__(self, app_id):
        """
        :param int app_id: The ID of the application, between 0 and 255
        """
        super().__init__(
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
