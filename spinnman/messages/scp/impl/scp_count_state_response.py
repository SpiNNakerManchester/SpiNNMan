from spinnman.messages.scp.abstract_messages.abstract_scp_response \
    import AbstractSCPResponse
from spinnman.messages.scp.scp_result import SCPResult
from spinnman.exceptions import SpinnmanUnexpectedResponseCodeException


class SCPCountStateResponse(AbstractSCPResponse):
    """ An SCP response to a request for the number of cores in a given state
    """

    def __init__(self):
        """
        """
        super(SCPCountStateResponse, self).__init__()
        self._count = None

    def read_scp_response(self, byte_reader):
        """ See :py:meth:`spinnman.messages.scp.abstract_scp_response.AbstractSCPResponse.read_scp_response`
        """
        super(SCPCountStateResponse, self).read_scp_response(byte_reader)
        result = self.scp_response_header.result
        if result != SCPResult.RC_OK:
            raise SpinnmanUnexpectedResponseCodeException(
                "CountState", "CMD_SIGNAL", result.name)
        self._count = byte_reader.read_int()

    @property
    def count(self):
        """ The count of the number of cores with the requested state

        :rtype: int
        """
        return self._count
