from spinnman.messages.scp.abstract_messages import AbstractSCPResponse
from spinnman.messages.scp.enums import SCPResult
from spinnman.exceptions import SpinnmanUnexpectedResponseCodeException


class CheckOKResponse(AbstractSCPResponse):
    """ An SCP response to a request which returns nothing other than OK
    """

    def __init__(self, operation, command):
        """

        :param operation: The operation being performed
        :type operation: str
        :param command: The command that was sent
        :type command: str
        """
        super(CheckOKResponse, self).__init__()
        self._operation = operation
        self._command = command

    def read_data_bytestring(self, data, offset):
        """ See\
            :py:meth:`spinnman.messages.scp.abstract_scp_response.AbstractSCPResponse.read_data_bytestring`
        """
        result = self.scp_response_header.result
        if result != SCPResult.RC_OK:
            raise SpinnmanUnexpectedResponseCodeException(
                self._operation, self._command, result.name)
