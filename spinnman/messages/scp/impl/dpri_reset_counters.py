from spinnman.messages.scp import SCPRequestHeader
from spinnman.messages.scp.abstract_messages import AbstractSCPRequest
from spinnman.messages.scp.enums import SCPCommand, SCPDPRICommand
from spinnman.messages.sdp import SDPFlag, SDPHeader
from .check_ok_response import SCPCheckOKResponse


class SCPDPRIResetCountersRequest(AbstractSCPRequest):
    """ An SCP Request to reset the statistics counters of the dropped packet\
        reinjection
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
                flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                destination_cpu=p, destination_chip_x=x,
                destination_chip_y=y),
            SCPRequestHeader(command=SCPCommand.CMD_DPRI),
            argument_1=SCPDPRICommand.RESET_COUNTERS.value)

    def get_scp_response(self):
        return SCPCheckOKResponse("Reset dropped packet reinjection counters",
                                  SCPCommand.CMD_DPRI)