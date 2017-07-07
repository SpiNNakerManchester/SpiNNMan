from spinnman.messages.scp import SCPRequestHeader
from spinnman.messages.scp.abstract_messages import AbstractSCPRequest
from spinnman.messages.scp.enums import SCPCommand
from spinnman.messages.sdp import SDPFlag, SDPHeader
from .check_ok_response import CheckOKResponse


class SetLED(AbstractSCPRequest):
    """ A request to change the state of an SetLED
    """

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

    def get_scp_response(self):
        """ See\
            :py:meth:`spinnman.messages.scp.abstract_scp_request.AbstractSCPRequest.get_scp_response`
        """
        return CheckOKResponse("Set SetLED", "CMD_LED")
