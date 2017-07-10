from spinnman.messages.scp.abstract_messages import AbstractSCPResponse
from spinnman.messages.scp.enums import SCPResult
from spinnman.exceptions import SpinnmanUnexpectedResponseCodeException
from spinnman.model import ChipSummaryInfo


class GetChipInfoResponse(AbstractSCPResponse):
    """ An SCP response to a request for the version of software running
    """

    def __init__(self):
        """
        """
        AbstractSCPResponse.__init__(self)
        self._chip_info = None

    def read_data_bytestring(self, data, offset):
        """ See\
            :py:meth:`spinnman.messages.scp.abstract_scp_response.AbstractSCPResponse.read_data_bytestring`
        """
        result = self.scp_response_header.result
        if result != SCPResult.RC_OK:
            raise SpinnmanUnexpectedResponseCodeException(
                "Version", "CMD_CHIP_INFO", result.name)
        self._chip_info = ChipSummaryInfo(
            data, offset, self.sdp_header.source_chip_x,
            self.sdp_header.source_chip_y,)

    @property
    def chip_info(self):
        """ The chip information received

        :rtype: :py:class:`spinnman.model.chip_summary_info.ChipSummaryInfo`
        """
        return self._chip_info
