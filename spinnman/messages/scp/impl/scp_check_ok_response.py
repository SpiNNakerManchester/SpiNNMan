from spinnman.messages.scp.abstract_messages.abstract_scp_response \
    import AbstractSCPResponse
from spinnman.messages.scp.scp_result import SCPResult
from spinnman.exceptions import SpinnmanUnexpectedResponseCodeException


class SCPCheckOKResponse(AbstractSCPResponse):
    """ An SCP response to a request which returns nothing other than OK
    """

    def __init__(self, operation, command):
        """

        :param operation: The operation being performed
        :type operation: str
        :param command: The command that was sent
        :type command: str
        """
        super(SCPCheckOKResponse, self).__init__()
        self._operation = operation
        self._command = command

    def read_scp_response(self, byte_reader):
        """ See :py:meth:`spinnman.messages.scp.abstract_scp_response.AbstractSCPResponse.read_scp_response`
        """
        super(SCPCheckOKResponse, self).read_scp_response(byte_reader)
        result = self.scp_response_header.result
        if result != SCPResult.RC_OK:
            raise SpinnmanUnexpectedResponseCodeException(
                self._operation, self._command, result.name)
