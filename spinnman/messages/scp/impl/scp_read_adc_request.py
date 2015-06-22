"""
ScpReadAdcRequest
"""
from spinnman import constants
from spinnman.messages.scp.abstract_messages.abstract_scp_bmp_request import \
    AbstractSCPBMPRequest
from spinnman.messages.scp.impl.scp_read_adc_response import SCPReadADCResponse
from spinnman.messages.scp.scp_command import SCPCommand
from spinnman.messages.scp.scp_request_header import SCPRequestHeader


class SCPReadADCRequest(AbstractSCPBMPRequest):
    """ SCP Request for the data from the BMP including voltages and\
        temperature.
    """

    def __init__(self, board):
        """

        :param board: which board to request the adc register from
        :return:
        """
        AbstractSCPBMPRequest.__init__(
            self, board,
            SCPRequestHeader(command=SCPCommand.CMD_BMP_INFO),
            argument_1=constants.BMP_INFO_TYPE.ADC)

    def get_scp_response(self):
        """
        """
        return SCPReadADCResponse()
