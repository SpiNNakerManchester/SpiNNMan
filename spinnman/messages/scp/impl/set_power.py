import logging
from spinn_utilities.overrides import overrides
from spinnman.messages.scp.abstract_messages \
    import AbstractSCPRequest, BMPRequest
from spinnman.messages.scp.enums import SCPCommand
from spinnman.messages.scp import SCPRequestHeader
from .check_ok_response import CheckOKResponse

logger = logging.getLogger(__name__)


class SetPower(BMPRequest):
    """ An SCP request for the BMP to power on or power off a rack of boards
    """
    __slots__ = []

    def __init__(self, power_command, boards, delay=0.0, board_to_send_to=0):
        """
        .. note::
            There is currently a bug in the BMP that means some boards don't\
            respond to power commands not sent to BMP 0. Thus changing the\
            board_to_send_to parameter is not recommended!

        :param power_command: The power command being sent
        :type power_command:\
            :py:class:`spinnman.messages.scp.scp_power_command.SCPPowerCommand`
        :param boards: The boards on the same backplane to power on or off
        :type boards: int or iterable of int
        :param delay: Number of seconds delay between power state changes of\
            the different boards.
        :type delay: int
        :param board_to_send_to: The optional board to send the command to if\
            this is to be sent to a frame of boards.
        :type: board_to_send_to: 0
        :rtype: None
        """

        if board_to_send_to != 0:
            logger.warning(
                "There is currently a bug in the BMP that means some boards"
                " don't respond to power commands not sent to BMP 0.  Thus "
                "changing the board_to_send_to is not recommended!")

        arg1 = (int(delay * 1000) << 16) | power_command.value
        arg2 = self.get_board_mask(boards)

        super(SetPower, self).__init__(
            board_to_send_to,
            SCPRequestHeader(command=SCPCommand.CMD_BMP_POWER),
            argument_1=arg1, argument_2=arg2)

    @overrides(AbstractSCPRequest.get_scp_response)
    def get_scp_response(self):
        """ Get the response from the powering message
        """
        return CheckOKResponse("powering request", "CMD_BMP_POWER")
