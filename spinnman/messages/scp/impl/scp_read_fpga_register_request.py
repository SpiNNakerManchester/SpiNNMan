"""
SCPReadFPGARegisterRequest
"""

# spinnman imports
from spinnman.messages.scp.abstract_messages.abstract_scp_bmp_request import \
    AbstractSCPBMPRequest
from spinnman.messages.scp.impl.scp_read_fpga_register_response import \
    SCPReadFPGARegisterResponse
from spinnman.messages.scp.enums.scp_command import SCPCommand
from spinnman.messages.scp.scp_request_header import SCPRequestHeader


class SCPReadFPGARegisterRequest(AbstractSCPBMPRequest):
    """ Requests the data from a fpga's register
    """

    def __init__(self, fpga_num, register, board):
        """
        sets up a read fpga register request

        :param fpga_num: FPGA number (0, 1 or 2) to communicate with.
        :param register: Register address to read to (will be rounded down to
                the nearest 32-bit word boundary).
        :param board: which board to request the fpga register from
        :rtype: None
        """

        # check to stop people asking for none word aligned memory addresses
        # inverses all bits of a value, so is basically a inverse mask for the
        # value entered.
        arg1 = register & (~0x3)
        AbstractSCPBMPRequest.__init__(
            self, board,
            SCPRequestHeader(
                command=SCPCommand.CMD_LINK_READ),
            argument_1=arg1, argument_2=4, argument_3=fpga_num)

    def get_scp_response(self):
        return SCPReadFPGARegisterResponse()
