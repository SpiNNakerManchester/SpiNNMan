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
from spinnman.messages.scp.abstract_messages import (
    AbstractSCPRequest, BMPRequest)
from spinnman.messages.scp.enums import SCPCommand
from .check_ok_response import CheckOKResponse


class BMPSetLed(BMPRequest):
    """ Set the LED(s) of a board to either on, off or toggling
    """
    __slots__ = []

    def __init__(self, led, action, boards):
        """

        :param led: Number of the LED or an iterable of LEDs to set the\
            state of (0-7)
        :type led: int or iterable of int
        :param action: State to set the LED to, either on, off or toggle
        :type action:\
            :py:class:`spinnman.messages.scp.enums.led_action.SCPLEDAction`
        :param boards: Specifies the board to control the LEDs of. This may\
            also be an iterable of multiple boards (in the same frame).
        :type boards: int or iterable of int
        :rtype: None
        """

        # set up the led entry for arg1
        if isinstance(led, int):
            leds = [led]
        else:
            leds = led

        # LED setting actions
        arg1 = sum(action.value << (led * 2) for led in leds)

        # Bitmask of boards to control
        arg2 = self.get_board_mask(boards)

        # initialise the request now
        super(BMPSetLed, self).__init__(
            boards,
            SCPRequestHeader(command=SCPCommand.CMD_LED),
            argument_1=arg1, argument_2=arg2)

    @overrides(AbstractSCPRequest.get_scp_response)
    def get_scp_response(self):
        """ Get the response from the write FPGA register request
        """
        return CheckOKResponse("Set the LEDs of a board", "CMD_LED")
