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


class SetLED(AbstractSCPRequest):
    """ A request to change the state of an SetLED
    """
    __slots__ = []

    def __init__(self, x, y, cpu, led_states):
        """
        :param x: The x-coordinate of the chip, between 0 and 255
        :type x: int
        :param y: The y-coordinate of the chip, between 0 and 255
        :type y: int
        :param cpu: The CPU-number to use to set the SetLED.
        :type cpu: int
        :param led_states: \
            A dictionary mapping SetLED index to state with\
            0 being off, 1 on and 2 inverted.
        :type led_states: dict
        """
        encoded_led_states = 0
        for led, state in led_states.items():
            encoded_led_states |= {0: 2, 1: 3, 2: 1}[state] << (2 * led)

        super(SetLED, self).__init__(
            SDPHeader(
                flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                destination_cpu=cpu, destination_chip_x=x,
                destination_chip_y=y),
            SCPRequestHeader(command=SCPCommand.CMD_LED),
            argument_1=encoded_led_states)

    @overrides(AbstractSCPRequest.get_scp_response)
    def get_scp_response(self):
        return CheckOKResponse("Set SetLED", "CMD_LED")
