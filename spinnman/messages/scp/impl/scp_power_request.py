"""
SCPPowerRequest
"""

# spinnman imports
from spinnman.messages.scp.abstract_messages.abstract_scp_bmp_request import \
    AbstractSCPBMPRequest
from spinnman.messages.scp.impl.scp_check_ok_response import SCPCheckOKResponse
from spinnman.messages.scp.scp_command import SCPCommand
from spinnman.messages.scp.scp_request_header import SCPRequestHeader
from spinnman.messages.sdp.sdp_flag import SDPFlag
from spinnman.messages.sdp.sdp_header import SDPHeader

class SCPPowerRequest(AbstractSCPBMPRequest):
    """
    the scp request for the bmp to power on or power off a rack of boards
    """

    def __init__(self, state, board, delay=0.0):
        """
        message that powers up or powers down a rack of spinnaker boards
        :param state: bool which says if the packet is powering up or down the
        rack of spinnaker boards
        :type state: boolean
        :param board: the position of the boards in the rack that are to be
            powered on or off by this message
        :type board: list of iterables or int
        :param delay: Number of seconds delay between power state changes of
            different boards.
        :type delay: int
        :return:
        """
        if isinstance(board, int):
            boards = [board]
        else:
            boards = list(board)
            board = boards[0]

        arg1 = int(delay * 1000) << 16
        if state:
            arg1 |= 1
        else:
            arg1 |= 0

        arg2 = sum(1 << b for b in boards)

        AbstractSCPBMPRequest.__init__(
            self, SDPHeader(
                flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                destination_cpu=board, destination_chip_x=0,
                destination_chip_y=0),
            SCPRequestHeader(command=SCPCommand.CMD_BMP_POWER),
            argument_1=arg1, argument_2=arg2)

    def get_scp_response(self):
        """
        gets the response from the powering message
        :return:
        """
        return SCPCheckOKResponse("powering request", "CMD_BMP_POWER")
