"""
SCPBMPSetLedRequest
"""
from spinnman import constants
from spinnman.messages.scp.abstract_messages.abstract_scp_bmp_request import \
    AbstractSCPBMPRequest
from spinnman.messages.scp.impl.scp_check_ok_response import SCPCheckOKResponse
from spinnman.messages.scp.scp_command import SCPCommand
from spinnman.messages.scp.scp_request_header import SCPRequestHeader
from spinnman.messages.sdp.sdp_flag import SDPFlag
from spinnman.messages.sdp.sdp_header import SDPHeader


class SCPBMPSetLedRequest(AbstractSCPBMPRequest):
    """
    request to set the led(s) of a board to either on, off or toggling
    """

    def __init__(self, led, action, board):
        """

        :param led: Number of the LED or an iterable of LEDs to set the
        state of (0-7)
        :type led: int or iterable
        :param action: State to set the LED to, either on, off or toggle
        :type action: enum of LEDS_ACTIONS
        :param board: Specifies the board to control the LEDs of. This may also be an
            iterable of multiple boards (in the same frame). The command will
            actually be sent to the first board in the iterable.
        :type board: int or iterable
        :return: None
        """

        # set up the led entry for arg1
        if isinstance(led, int):
            leds = [led]
        else:
            leds = led

        # set up the board entity for generating the arg2 entry
        if isinstance(board, int):
            boards = [board]
        else:
            boards = list(board)
            board = boards[0]

        # LED setting actions
        arg1 = sum(action.value << (led * 2) for led in leds)

        # Bitmask of boards to control
        arg2 = sum(1 << b for b in boards)

        # initilise the request now
        AbstractSCPBMPRequest.__init__(
            self,
            SDPHeader(
                flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                destination_cpu=board, destination_chip_x=0,
                destination_chip_y=0),
            SCPRequestHeader(command=SCPCommand.CMD_LED),
            argument_1=arg1, argument_2=arg2)

    def get_scp_response(self):
        """
        gets the response from the write fpga register request
        :return:
        """
        return SCPCheckOKResponse("Set the leds of a board", "CMD_LED")