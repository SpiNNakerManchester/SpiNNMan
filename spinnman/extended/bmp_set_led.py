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

from typing import Iterable, Union
from spinn_utilities.overrides import overrides
from spinnman.messages.scp import SCPRequestHeader
from spinnman.messages.scp.abstract_messages import (
    AbstractSCPRequest, BMPRequest)
from spinnman.messages.scp.enums import SCPCommand
from spinnman.messages.scp.impl.check_ok_response import CheckOKResponse
from spinnman.messages.scp.enums.led_action import LEDAction


class BMPSetLed(BMPRequest):
    """
    Set the LED(s) of a board to either on, off or toggling.

    This class is currently deprecated and untested as there is no
    known use except for Transceiver.set_led which is itself deprecated.
    """
    __slots__ = ()

    def __init__(self, led: Union[int, Iterable[int]], action: LEDAction,
                 boards: Union[int, Iterable[int]]):
        """
        :param led: Number of the LED or an iterable of LEDs to set the
            state of (0-7)
        :param action:
            State to set the LED to, either on, off or toggle
        :param boards: Specifies the board to control the LEDs of. This may
            also be an iterable of multiple boards (in the same frame).
        """
        # set up the led entry for arg1
        if isinstance(led, int):
            arg1 = action.value << (led * 2)
        else:
            arg1 = sum(action.value << (a_led * 2) for a_led in led)

        # Bitmask of boards to control
        arg2 = self.get_board_mask(boards)

        # initialise the request now
        super().__init__(
            boards,
            SCPRequestHeader(command=SCPCommand.CMD_LED),
            argument_1=arg1, argument_2=arg2)

    @overrides(AbstractSCPRequest.get_scp_response)
    def get_scp_response(self) -> CheckOKResponse:
        return CheckOKResponse("Set the LEDs of a board", "CMD_LED")
