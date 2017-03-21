from spinnman.messages.scp.abstract_messages.abstract_scp_bmp_reponse import \
    AbstractSCPBMPResponse
from spinnman.messages.scp.enums.scp_result import SCPResult
from spinnman.exceptions import SpinnmanUnexpectedResponseCodeException
from spinnman.model.adc_info import ADCInfo


class SCPReadADCResponse(AbstractSCPBMPResponse):
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
