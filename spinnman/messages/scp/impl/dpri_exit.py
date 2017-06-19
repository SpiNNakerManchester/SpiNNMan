from spinnman.messages.scp import SCPRequestHeader
from spinnman.messages.scp.abstract_messages import AbstractSCPRequest
from spinnman.messages.scp.enums import SCPCommand, SCPDPRICommand
from spinnman.messages.sdp import SDPFlag, SDPHeader
from .check_ok_response import SCPCheckOKResponse


class SCPDPRIExitRequest(AbstractSCPRequest):
    """ An SCP Request to exit the dropped packet reinjection
    """

    def __init__(self, x, y, p):
        """
        :param x: The x-coordinate of a chip, between 0 and 255
        :type x: int
        :param y: The y-coordinate of a chip, between 0 and 255
        :type y: int
        :param p: The processor running the dropped packet reinjector, between\
                0 and 17
        :type p: int
        """
        AbstractSCPRequest.__init__(
            self,
            SDPHeader(
                flags=SDPFlag.REPLY_EXPECTED, port=0,
                destination_cpu=p, destination_chip_x=x,
                destination_chip_y=y),
            SCPRequestHeader(command=SCPCommand.CMD_DPRI),
            argument_1=SCPDPRICommand.EXIT.value)

    def get_scp_response(self):
        return SCPCheckOKResponse("Exit dropped packet reinjection",
                                  SCPCommand.CMD_DPRI)
