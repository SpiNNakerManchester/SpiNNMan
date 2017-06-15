"""
ScpReadAdcRequest
"""
from spinnman.messages.scp.abstract_messages import AbstractSCPBMPRequest
from spinnman.messages.scp.enums import SCPBMPInfoType, SCPCommand
from spinnman.messages.scp import SCPRequestHeader
from .scp_read_adc_response import SCPReadADCResponse


class SCPReadADCRequest(AbstractSCPBMPRequest):
    """ SCP Request for the data from the BMP including voltages and\
        temperature.
    """

    def __init__(self, board):
        """

        :param board: which board to request the adc register from
        :rtype: None
        """
        AbstractSCPBMPRequest.__init__(
            self, board,
            SCPRequestHeader(command=SCPCommand.CMD_BMP_INFO),
            argument_1=SCPBMPInfoType.ADC)

    def get_scp_response(self):
        """
        """
        return SCPReadADCResponse()
