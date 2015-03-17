from spinnman.messages.scp.abstract_messages.abstract_scp_request import AbstractSCPRequest
from spinnman.messages.sdp.sdp_header import SDPHeader
from spinnman.messages.sdp.sdp_flag import SDPFlag
from spinnman.messages.scp.scp_request_header import SCPRequestHeader
from spinnman.messages.scp.scp_command import SCPCommand
from spinnman.messages.scp.impl.scp_iptag_info_response import SCPIPTagInfoResponse

_IPTAG_INFO = 4
_IPTAG_MAX = 255


class SCPTagInfoRequest(AbstractSCPRequest):
    """ An SCP Request information about IP tags
    """

    def __init__(self, x, y):
        """
        :param x: The x-coordinate of a chip, between 0 and 255
        :type x: int
        :param y: The y-coordinate of a chip, between 0 and 255
        :type y: int
        :raise spinnman.exceptions.SpinnmanInvalidParameterException:\
                    The chip-coordinates are out of range
        """
        super(SCPTagInfoRequest, self).__init__(
            SDPHeader(
                flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                destination_cpu=0, destination_chip_x=x,
                destination_chip_y=y),
            SCPRequestHeader(command=SCPCommand.CMD_IPTAG),
            argument_1=(_IPTAG_INFO << 16),
            argument_2=_IPTAG_MAX)

    def get_scp_response(self):
        return SCPIPTagInfoResponse()
