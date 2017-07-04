from spinnman.messages.scp.abstract_messages.abstract_scp_request\
    import AbstractSCPRequest
from spinnman.messages.sdp.sdp_header import SDPHeader
from spinnman.messages.sdp.sdp_flag import SDPFlag
from spinnman.messages.scp.scp_request_header import SCPRequestHeader
from spinnman.messages.scp.enums.scp_command import SCPCommand
from spinnman.messages.scp.enums.scp_dpri_command import SCPDPRICommand
from spinnman.messages.scp.impl.scp_check_ok_response import SCPCheckOKResponse


class SCPDPRISetRouterTimeoutRequest(AbstractSCPRequest):
    """ An SCP Request to set the router timeout for dropped packet reinjection
    """

    def __init__(self, x, y, p, timeout_mantissa, timeout_exponent):
        """
        :param x: The x-coordinate of a chip, between 0 and 255
        :type x: int
        :param y: The y-coordinate of a chip, between 0 and 255
        :type y: int
        :param p: The processor running the dropped packet reinjector, between\
                0 and 17
        :type p: int
        :param timeout_mantissa: The mantissa of the timeout value, \
                between 0 and 15
        :type timeout_mantissa: int
        :param timeout_exponent: The exponent of the timeout value, \
                between 0 and 15
        """
        AbstractSCPRequest.__init__(
            self,
            SDPHeader(
                flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                destination_cpu=p, destination_chip_x=x,
                destination_chip_y=y),
            SCPRequestHeader(command=SCPCommand.CMD_DPRI),
            argument_1=SCPDPRICommand.SET_ROUTER_TIMEOUT.value,
            argument_2=(timeout_mantissa & 0xF) |
                       ((timeout_exponent & 0xF) << 4))

    def get_scp_response(self):
        return SCPCheckOKResponse("Set router timeout", SCPCommand.CMD_DPRI)
