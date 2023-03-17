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
from .check_ok_response import CheckOKResponse


class SetLED(AbstractSCPRequest):
    """
    A request to change the state of an SetLED.

    This class is currently deprecated and untested as there is no
    known use except for Transceiver.set_led which is itself deprecated.
    """
    __slots__ = []

    def __init__(self, x, y, cpu, led_states):
        """
        :param int x: The x-coordinate of the chip, between 0 and 255
        :param int y: The y-coordinate of the chip, between 0 and 255
        :param int cpu: The CPU-number to use to set the SetLED.
        :param dict(int,int) led_states:
            A dictionary mapping SetLED index to state with
            0 being off, 1 on and 2 inverted.
        """
        encoded_led_states = 0
        for led, state in led_states.items():
            encoded_led_states |= {0: 2, 1: 3, 2: 1}[state] << (2 * led)

        super().__init__(
            SDPHeader(
                flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                destination_cpu=cpu, destination_chip_x=x,
                destination_chip_y=y),
            SCPRequestHeader(command=SCPCommand.CMD_LED),
            argument_1=encoded_led_states)

    @overrides(AbstractSCPRequest.get_scp_response)
    def get_scp_response(self):
        return CheckOKResponse("Set SetLED", "CMD_LED")
