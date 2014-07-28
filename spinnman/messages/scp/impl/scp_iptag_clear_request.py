from spinnman.messages.scp.abstract_messages.abstract_scp_request import AbstractSCPRequest
from spinnman.messages.sdp.sdp_header import SDPHeader
from spinnman.messages.sdp.sdp_flag import SDPFlag
from spinnman.messages.scp.scp_request_header import SCPRequestHeader
from spinnman.messages.scp.scp_command import SCPCommand
from spinnman.exceptions import SpinnmanInvalidParameterException
from spinnman.messages.scp.impl.scp_check_ok_response import SCPCheckOKResponse

_IPTAG_CLEAR = 3


class SCPIPTagClearRequest(AbstractSCPRequest):
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
        :raise spinnman.exceptions.SpinnmanInvalidParameterException:
                    * The chip-coordinates are out of range
                    * If the tag is not between 0 and 7
        """
        if tag < 0 or tag > 7:
            raise SpinnmanInvalidParameterException(
                "tag", str(tag), "Must be between 0 and 7")

        super(SCPIPTagClearRequest, self).__init__(
            SDPHeader(
                flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                destination_cpu=0, destination_chip_x=x,
                destination_chip_y=y),
            SCPRequestHeader(command=SCPCommand.CMD_IPTAG),
            argument_1=(_IPTAG_CLEAR << 16) | tag)

    def get_scp_response(self):
        return SCPCheckOKResponse("Clear IP Tag", "CMD_IPTAG")
