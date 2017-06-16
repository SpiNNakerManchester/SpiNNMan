"""
ScpReadAdcRequest
"""
from spinnman.messages.scp import SCPRequestHeader
from spinnman.messages.scp.abstract_messages \
    import AbstractSCPBMPRequest, AbstractSCPBMPResponse
from spinnman.messages.scp.enums \
    import SCPBMPInfoType, SCPCommand, SCPResult
from spinnman.exceptions import SpinnmanUnexpectedResponseCodeException
from spinnman.model import ADCInfo


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
        return _SCPReadADCResponse()


class _SCPReadADCResponse(AbstractSCPBMPResponse):
    """ An SCP response to a request for ADC information
    """

    def __init__(self):
        """
        """
        AbstractSCPBMPResponse.__init__(self)
        self._adc_info = None

    def read_data_bytestring(self, data, offset):
        """ See\
            :py:meth:`spinnman.messages.scp.abstract_scp_response.AbstractSCPResponse.read_data_bytestring`
        """
        result = self.scp_response_header.result
        if result != SCPResult.RC_OK:
            raise SpinnmanUnexpectedResponseCodeException(
                "ADC", "CMD_ADC", result.name)
        self._adc_info = ADCInfo(data, offset)

    @property
    def adc_info(self):
        """ The ADC information
        """
        return self._adc_info
