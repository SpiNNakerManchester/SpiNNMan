from spinnman.messages.scp.abstract_messages.abstract_scp_response\
    import AbstractSCPResponse
from spinnman.model.dpri_status import DPRIStatus
from spinnman.exceptions import SpinnmanUnexpectedResponseCodeException
from spinnman.messages.scp.enums.scp_result import SCPResult
from spinnman.messages.scp.enums.scp_command import SCPCommand


class SCPDPRIGetStatusResponse(AbstractSCPResponse):
    """ An SCP response to a request for the dropped packet reinjection status
    """

    def __init__(self):
        """
        """
        AbstractSCPResponse.__init__(self)
        self._dpri_status = None

    def read_data_bytestring(self, data, offset):
        """ See\
            :py:meth:`spinnman.messages.scp.abstract_scp_response.AbstractSCPResponse.read_data_bytestring`
        """
        result = self.scp_response_header.result
        if result != SCPResult.RC_OK:
            raise SpinnmanUnexpectedResponseCodeException(
                "Get dropped packet reinjection status", SCPCommand.CMD_DPRI,
                result.name)
        self._dpri_status = DPRIStatus(data, offset)

    @property
    def dpri_status(self):
        return self._dpri_status
