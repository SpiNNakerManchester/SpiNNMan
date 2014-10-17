from spinnman.messages.scp.abstract_messages.abstract_scp_request import AbstractSCPRequest
from spinnman.messages.sdp.sdp_header import SDPHeader
from spinnman.messages.sdp.sdp_flag import SDPFlag
from spinnman.messages.scp.scp_request_header import SCPRequestHeader
from spinnman.messages.scp.scp_command import SCPCommand
from spinnman.exceptions import SpinnmanInvalidParameterException
from spinnman.messages.scp.impl.scp_check_ok_response import SCPCheckOKResponse

_IPTAG_SET = 1


class SCPIPTagSetRequest(AbstractSCPRequest):
    """ An SCP Request to set an IP Tag
    """

    def __init__(self, x, y, host, port, tag, strip):
        """
        :param x: The x-coordinate of a chip, between 0 and 255
        :type x: int
        :param y: The y-coordinate of a chip, between 0 and 255
        :type y: int
        :param host: The host address, as an array of 4 bytes
        :type host: bytearray
        :param port: The port, between 0 and 65535
        :type port: int
        :param tag: The tag, between 0 and 7
        :type tag: int
        :param strip: if the SDP header should be striped from the packet.
        :type strip: bool
        :raise spinnman.exceptions.SpinnmanInvalidParameterException:
                    * The chip-coordinates are out of range
                    * If the host is not 4 bytes
                    * If the port is not between 0 and 65535
                    * If the tag is not between 0 and 7
        """
        if len(host) != 4:
            raise SpinnmanInvalidParameterException(
                "len(host)", str(len(host)), "Must be 4 bytes")
        if port < 0 or port > 65535:
            raise SpinnmanInvalidParameterException(
                "port", str(port), "Must be between 0 and 65535")
        if tag < 0 or tag > 7:
            raise SpinnmanInvalidParameterException(
                "tag", str(tag), "Must be between 0 and 7")

        strip_value = 0
        if strip:
            strip_value = 1

        super(SCPIPTagSetRequest, self).__init__(
            SDPHeader(
                flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                destination_cpu=0, destination_chip_x=x,
                destination_chip_y=y),
            SCPRequestHeader(command=SCPCommand.CMD_IPTAG),
            argument_1=(strip_value << 28) | (_IPTAG_SET << 16) | tag,
            argument_2=port,
            argument_3=((host[3] << 24) | (host[2] << 16)
                        | (host[1] << 8) | host[0]))

    def get_scp_response(self):
        return SCPCheckOKResponse("Set IP Tag", "CMD_IPTAG")
