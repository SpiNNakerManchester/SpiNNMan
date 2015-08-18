from spinnman.messages.scp.abstract_messages.abstract_scp_response\
    import AbstractSCPResponse
from spinnman.model.dpri_status import DPRIStatus


class SCPDPRIGetStatusResponse(AbstractSCPResponse):
    """ An SCP response to a request for the dropped packet reinjection status
    """

    def __init__(self):
        """
        """
        AbstractSCPResponse.__init__()
        self._dpri_status

    def read_data_bytestring(self, data, offset):
        """ See\
            :py:meth:`spinnman.messages.scp.abstract_scp_response.AbstractSCPResponse.read_data_bytestring`
        """
        self._dpri_status = DPRIStatus(data, offset)

    @property
    def dpri_status(self):
        return self._dpri_status
