from spinnman.messages.scp import SCPRequestHeader
from spinnman.messages.scp.abstract_messages import AbstractSCPRequest
from spinnman.messages.scp.enums import SCPCommand
from spinnman.messages.sdp import SDPFlag, SDPHeader
from .check_ok_response import CheckOKResponse


class RouterClear(AbstractSCPRequest):
    """ A request to clear the router on a chip
    """

    def __init__(self, x, y):
        """

        :param x: The x-coordinate of the chip, between 0 and 255 \
        this is not checked due to speed restrictions
        :type x: int
        :param y: The y-coordinate of the chip, between 0 and 255 \
        this is not checked due to speed restrictions
        :type y: int
        :raise spinnman.exceptions.SpinnmanInvalidParameterException:\
                    * If x is out of range
                    * If y is out of range
        """
        super(RouterClear, self).__init__(
            SDPHeader(
                flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                destination_cpu=0, destination_chip_x=x,
                destination_chip_y=y),
            SCPRequestHeader(command=SCPCommand.CMD_RTR))

    def get_scp_response(self):
        return CheckOKResponse("RouterClear", "CMD_RTR")
