"""
SCPBMPVersionRequest
"""

# spinnman imports
from spinnman.messages.scp.abstract_messages.abstract_scp_bmp_request import \
    AbstractSCPBMPRequest
from spinnman.messages.scp.impl.scp_bmp_version_response import \
    SCPBMPVersionResponse
from spinnman.messages.scp.impl.scp_version_request import SCPVersionRequest

from spinnman.messages.sdp.sdp_flag import SDPFlag
from spinnman.messages.sdp.sdp_header import SDPHeader
from spinnman.messages.scp.scp_request_header import SCPRequestHeader
from spinnman.messages.scp.scp_command import SCPCommand


class SCPBMPVersionRequest(AbstractSCPBMPRequest, SCPVersionRequest):
    """ An SCP request to read the version of software running on a core
    """

    def __init__(self, board):
        """

        :param x: The x-coordinate of the chip to read from, between 0 and 255
        :type x: int
        :param y: The y-coordinate of the chip to read from, between 0 and 255
        :type y: int
        :param p: The id of the processor to read the version from,\
                    between 0 and 31
        :type p: int
        :param bmp_ip_address: the bmp ip address to which this message needs
        to be sent
        :raise spinnman.exceptions.SpinnmanInvalidParameterException:
                    * If the chip coordinates are out of range
                    * If the processor is out of range
        """
        AbstractSCPBMPRequest.__init__(
            self,
            SDPHeader(
                flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                destination_cpu=board, destination_chip_x=0,
                destination_chip_y=0),
            SCPRequestHeader(command=SCPCommand.CMD_VER))

    def get_scp_response(self):
        """ See :py:meth:`spinnman.messages.scp.abstract_scp_request.AbstractSCPRequest.get_scp_response`
        """
        return SCPBMPVersionResponse()
