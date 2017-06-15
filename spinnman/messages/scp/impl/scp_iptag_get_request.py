from spinnman.messages.scp import SCPRequestHeader
from spinnman.messages.scp.abstract_messages import AbstractSCPRequest
from spinnman.messages.scp.enums import SCPCommand
from spinnman.messages.sdp import SDPFlag, SDPHeader
from .scp_iptag_get_response import SCPIPTagGetResponse

_IPTAG_GET = 2


class SCPTagGetRequest(AbstractSCPRequest):
    """ An SCP Request to get an IP tag
    """

    def __init__(self, x, y, tag):
        """
        :param x: The x-coordinate of a chip, between 0 and 255
        :type x: int
        :param y: The y-coordinate of a chip, between 0 and 255
        :type y: int
        :param tag: The tag to get details of, between 0 and 7
        :type tag: int
        :param tag: The tag, between 0 and 7
        :type tag: int
        """
        super(SCPTagGetRequest, self).__init__(
            SDPHeader(
                flags=SDPFlag.REPLY_EXPECTED, port=0,
                destination_cpu=0, destination_chip_x=x,
                destination_chip_y=y),
            SCPRequestHeader(command=SCPCommand.CMD_IPTAG),
            argument_1=(_IPTAG_GET << 16) | tag,
            argument_2=1)

    def get_scp_response(self):
        return SCPIPTagGetResponse()
