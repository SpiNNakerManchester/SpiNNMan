from spinnman.messages.scp import SCPRequestHeader
from spinnman.messages.scp.abstract_messages import AbstractSCPRequest
from spinnman.messages.scp.enums import SCPCommand
from spinnman.messages.sdp import SDPFlag, SDPHeader
from .check_ok_response import CheckOKResponse

_IPTAG_SET = 1


class ReverseIPTagSet(AbstractSCPRequest):
    """ An SCP Request to set an IP Tag
    """

    def __init__(self, x, y, destination_x, destination_y, destination_p, port,
                 tag, sdp_port):
        """
        :param x: The x-coordinate of a chip, between 0 and 255
        :type x: int
        :param y: The y-coordinate of a chip, between 0 and 255
        :type y: int
        :param destination_x: The x-coordinate of the destination chip,\
                    between 0 and 255
        :type destination_x: int
        :param destination_y: The y-coordinate of the destination chip,\
                    between 0 and 255
        :type destination_y: int
        :param destination_p: the id of the destination processor, between\
                    0 and 17
        :type destination_p: int
        :param port: The port, between 0 and 65535
        :type port: int
        :param tag: The tag, between 0 and 7
        :type tag: int
        """
        strip_value = 1
        reverse_value = 1

        arg1 = ((reverse_value << 29) | (strip_value << 28) |
                (_IPTAG_SET << 16) | (sdp_port << 13) | (destination_p << 8) |
                tag)
        arg2 = ((destination_x << 24) | (destination_y << 16) | port)

        super(ReverseIPTagSet, self).__init__(
            SDPHeader(
                flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                destination_cpu=0, destination_chip_x=x,
                destination_chip_y=y),
            SCPRequestHeader(command=SCPCommand.CMD_IPTAG),
            argument_1=arg1,
            argument_2=arg2,
            argument_3=0)

    def get_scp_response(self):
        return CheckOKResponse("Set Reverse IP Tag", "CMD_IPTAG")
