from spinnman.messages.scp.abstract_messages.abstract_scp_bmp_reponse import \
    AbstractSCPBMPResponse
from spinnman.messages.scp.scp_result import SCPResult
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

    def read_scp_response(self, byte_reader):
        """ See\
            :py:meth:`spinnman.messages.scp.abstract_scp_response.AbstractSCPResponse.read_scp_response`
        """
        AbstractSCPBMPResponse.read_scp_response(self, byte_reader)
        result = self.scp_response_header.result
        if result != SCPResult.RC_OK:
            raise SpinnmanUnexpectedResponseCodeException(
                "Version", "CMD_VER", result.name)
        data = byte_reader.read_bytes()
        self._adc_info = ADCInfo(data)

    @property
    def adc_info(self):
        """ The ADC information
        """
        return self._adc_info
