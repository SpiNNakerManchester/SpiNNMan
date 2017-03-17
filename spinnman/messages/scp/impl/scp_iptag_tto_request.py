from spinnman.messages.scp.impl.scp_iptag_info_response \
    import SCPIPTagInfoResponse
from spinnman.messages.scp.abstract_messages.abstract_scp_request \
    import AbstractSCPRequest
from spinnman.messages.sdp.sdp_flag import SDPFlag
from spinnman.messages.sdp.sdp_header import SDPHeader
from spinnman.messages.scp.scp_request_header import SCPRequestHeader
from spinnman.messages.scp.enums.scp_command import SCPCommand

_IPTAG_TTO = (4 << 16)


class SCPIPTagTTORequest(AbstractSCPRequest):
    """ An SCP request to set the transient timeout for future SCP requests
    """

    def __init__(self, x, y, tag_timeout):
        """

        :param x: The x-coordinate of the chip to run on, between 0 and 255
        :type x: int
        :param y: The y-coordinate of the chip to run on, between 0 and 255
        :type y: int
        :param tag_timeout: The timeout value, via the
            IPTAG_TIME_OUT_WAIT_TIMES enum located in spinnman.constants
        """

        super(SCPIPTagTTORequest, self).__init__(
            SDPHeader(flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                      destination_cpu=0, destination_chip_x=x,
                      destination_chip_y=y),
            SCPRequestHeader(command=SCPCommand.CMD_IPTAG),
            argument_1=_IPTAG_TTO, argument_2=tag_timeout)

    def get_scp_response(self):
        """ See\
            :py:meth:`spinnman.messages.scp.abstract_scp_request.AbstractSCPRequest.get_scp_response`
        """
        return SCPIPTagInfoResponse()
