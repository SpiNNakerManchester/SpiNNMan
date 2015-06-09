"""
ScpReadAdcRequest
"""
from spinnman import constants
from spinnman.messages.scp.abstract_messages.abstract_scp_bmp_request import \
    AbstractSCPBMPRequest
from spinnman.messages.scp.impl.scp_read_adc_response import SCPReadADCResponse
from spinnman.messages.scp.scp_command import SCPCommand
from spinnman.messages.scp.scp_request_header import SCPRequestHeader
from spinnman.messages.sdp.sdp_flag import SDPFlag
from spinnman.messages.sdp.sdp_header import SDPHeader


class ScpReadADCRequest(AbstractSCPBMPRequest):
    """
    requests the data from the BMP including voltages and temperature.
    """

    def __init__(self, board, fpga_num):
        """
        request that sends a packet asking to read the adc register of the
        fpga
        :param board: which board to request the fpga's adc register from
        :param fpga_num: the fpga of the board to request the adc register from
        :return:
        """
        AbstractSCPBMPRequest.__init__(
            self, SDPHeader(
                flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                destination_cpu=board, destination_chip_x=0,
                destination_chip_y=0),
            SCPRequestHeader(command=SCPCommand.CMD_BMP_INFO),
            argument_1=constants.BMP_INFO_TYPE.ADC, argument_2=4,
            argument_3=fpga_num)

    def get_scp_response(self):
        """
        gets the response from the write fpga register request
        :return:
        """
        return SCPReadADCResponse()