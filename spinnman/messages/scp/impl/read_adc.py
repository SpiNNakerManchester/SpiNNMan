from spinnman.messages.scp import SCPRequestHeader
from spinn_utilities import overrides
from spinnman.messages.scp.abstract_messages.scp_response import AbstractSCPResponse
from spinnman.messages.scp.abstract_messages.scp_request import AbstractSCPRequest
from spinnman.messages.scp.abstract_messages \
    import BMPRequest, BMPResponse
from spinnman.messages.scp.enums \
    import BMPInfo, SCPCommand, SCPResult
from spinnman.exceptions import SpinnmanUnexpectedResponseCodeException
from spinnman.model import ADCInfo


class ReadADC(BMPRequest):
    """ SCP Request for the data from the BMP including voltages and\
        temperature.
    """
    __slots__ = []

    def __init__(self, board):
        """
        :param board: which board to request the ADC register from
        :rtype: None
        """
        super(ReadADC, self).__init__(
            board,
            SCPRequestHeader(command=SCPCommand.CMD_BMP_INFO),
            argument_1=BMPInfo.ADC)

    @overrides(AbstractSCPRequest.get_scp_response)
    def get_scp_response(self):
        return _SCPReadADCResponse()


class _SCPReadADCResponse(BMPResponse):
    """ An SCP response to a request for ADC information
    """
    __slots__ = [
        "_adc_info"]

    def __init__(self):
        super(_SCPReadADCResponse, self).__init__()
        self._adc_info = None

    @overrides(AbstractSCPResponse.read_data_bytestring)
    def read_data_bytestring(self, data, offset):
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
