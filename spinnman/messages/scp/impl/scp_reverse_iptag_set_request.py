from spinnman.messages.scp.abstract_messages.abstract_scp_request \
    import AbstractSCPRequest
from spinnman.messages.sdp.sdp_header import SDPHeader
from spinnman.messages.sdp.sdp_flag import SDPFlag
from spinnman.messages.scp.scp_request_header import SCPRequestHeader
from spinnman.messages.scp.scp_command import SCPCommand
from spinnman.exceptions import SpinnmanInvalidParameterException
from spinnman.messages.scp.impl.scp_check_ok_response import SCPCheckOKResponse

_IPTAG_SET = 1


class SCPReverseIPTagSetRequest(AbstractSCPRequest):
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
        :raise spinnman.exceptions.SpinnmanInvalidParameterException:
                    * The chip-coordinates are out of range
                    * If the host is not 4 bytes
                    * If the port is not between 0 and 65535
                    * If the tag is not between 0 and 7
        """
        if port < 0 or port > 65535:
            raise SpinnmanInvalidParameterException(
                "port", str(port), "Must be between 0 and 65535")
        if tag < 0 or tag > 7:
            raise SpinnmanInvalidParameterException(
                "tag", str(tag), "Must be between 0 and 7")
        if destination_x < 0 or destination_x > 255:
            raise SpinnmanInvalidParameterException(
                "destination_x", str(destination_x),
                "Must be between 0 and 255")
        if destination_y < 0 or destination_y > 255:
            raise SpinnmanInvalidParameterException(
                "destination_y", str(destination_y),
                "Must be between 0 and 255")
        if destination_p < 0 or destination_p > 17:
            raise SpinnmanInvalidParameterException(
                "destination_p", str(destination_p),
                "Must be between 0 and 17")

        strip_value = 1
        reverse_value = 1

        arg1 = ((reverse_value << 29) | (strip_value << 28)
                | (_IPTAG_SET << 16) | (sdp_port << 13) | (destination_p << 8)
                | tag)
        arg2 = ((destination_x << 24) | (destination_y << 16) | port)

        super(SCPReverseIPTagSetRequest, self).__init__(
            SDPHeader(
                flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                destination_cpu=0, destination_chip_x=x,
                destination_chip_y=y),
            SCPRequestHeader(command=SCPCommand.CMD_IPTAG),
            argument_1=arg1,
            argument_2=arg2,
            argument_3=0)

    def get_scp_response(self):
        return SCPCheckOKResponse("Set Reverse IP Tag", "CMD_IPTAG")
