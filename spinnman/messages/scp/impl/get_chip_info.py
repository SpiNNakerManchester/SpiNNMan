from spinnman.messages.scp import SCPRequestHeader
from spinnman.messages.scp.abstract_messages import AbstractSCPRequest
from spinnman.messages.scp.enums import SCPCommand
from spinnman.messages.sdp import SDPFlag, SDPHeader
from .get_chip_info_response import GetChipInfoResponse


class GetChipInfo(AbstractSCPRequest):
    """ An SCP request to read the chip information from a core
    """

    def __init__(self, x, y, with_size=False):
        """

        :param x: The x-coordinate of the chip to read from, between 0 and 255
        :type x: int
        :param y: The y-coordinate of the chip to read from, between 0 and 255
        :type y: int
        :param with_size: True if the size should be included in the response,\
                    False if not
        :type with_size: bool
        """
        # Bits 0-4 + bit 6 = all information except size
        argument_1 = 0x5F
        if with_size:

            # Bits 0-6 = all information including size
            argument_1 = 0x7F

        AbstractSCPRequest.__init__(
            self, SDPHeader(
                flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                destination_cpu=0, destination_chip_x=x,
                destination_chip_y=y),
            SCPRequestHeader(command=SCPCommand.CMD_INFO),
            argument_1=argument_1)

    def get_scp_response(self):
        """ See\
            :py:meth:`spinnman.messages.scp.abstract_scp_request.AbstractSCPRequest.get_scp_response`
        """
        return GetChipInfoResponse()
