"""
BMPSetLed
"""
from spinnman.messages.scp import SCPRequestHeader
from spinnman.messages.scp.abstract_messages import BMPRequest
from spinnman.messages.scp.enums import SCPCommand
from .check_ok_response import CheckOKResponse


class BMPSetLed(BMPRequest):
    """ Set the led(s) of a board to either on, off or toggling
    """

    def __init__(self, led, action, boards):
        """

        :param led: Number of the LED or an iterable of LEDs to set the\
                state of (0-7)
        :type led: int or iterable of int
        :param action: State to set the LED to, either on, off or toggle
        :type action:\
                :py:class:`spinnman.messages.scp.scp_led_action.SCPLEDAction`
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

        # initilise the request now
        BMPRequest.__init__(
            self, boards,
            SCPRequestHeader(command=SCPCommand.CMD_LED),
            argument_1=arg1, argument_2=arg2)

    def get_scp_response(self):
        """ Get the response from the write fpga register request
        """
        return CheckOKResponse("Set the LEDs of a board", "CMD_LED")
