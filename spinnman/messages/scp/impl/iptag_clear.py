from spinnman.messages.scp import SCPRequestHeader
from spinnman.messages.scp.abstract_messages import AbstractSCPRequest
from spinnman.messages.scp.enums import SCPCommand
from spinnman.messages.sdp import SDPFlag, SDPHeader
from .check_ok_response import CheckOKResponse

_IPTAG_CLEAR = 3


class IPTagClear(AbstractSCPRequest):
    """ An SCP Request to clear an IP Tag
    """

    def __init__(self, x, y, tag):
        """
        :param x: The x-coordinate of a chip, between 0 and 255
        :type x: int
        :param y: The y-coordinate of a chip, between 0 and 255
        :type y: int
        :param tag: The tag, between 0 and 7
        :type tag: int
        """
        super(IPTagClear, self).__init__(
            SDPHeader(
                flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                destination_cpu=0, destination_chip_x=x,
                destination_chip_y=y),
            SCPRequestHeader(command=SCPCommand.CMD_IPTAG),
            argument_1=(_IPTAG_CLEAR << 16) | tag)

    def get_scp_response(self):
        return CheckOKResponse("Clear IP Tag", "CMD_IPTAG")
