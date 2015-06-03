"""
ScpReadAdcRequest
"""
from spinnman.messages.scp.abstract_messages.abstract_scp_bmp_request import \
    AbstractSCPBMPRequest
from spinnman.messages.scp.scp_command import SCPCommand
from spinnman.messages.scp.scp_request_header import SCPRequestHeader
from spinnman.messages.sdp.sdp_flag import SDPFlag
from spinnman.messages.sdp.sdp_header import SDPHeader


class ScpReadADCRequest(AbstractSCPBMPRequest):
    """
    requests the data from the BMP including voltages and temperature.
    """

    def __init__(self, board):
        super(ScpReadADCRequest, self).__init__(
            SDPHeader(
                flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                destination_cpu=board, destination_chip_x=0,
                destination_chip_y=0),
            SCPRequestHeader(command=SCPCommand.CMD_BMP_INFO),
            argument_1=addr & (~0x3), argument_2=4, argument_3=fpga_num,
            data=struct.pack("<I", value))

    def get_scp_response(self):
        """
        gets the response from the write fpga register request
        :return:
        """
        return SCPCheckOKResponse("Send FPGA register write", "CMD_LINK_WRITE")