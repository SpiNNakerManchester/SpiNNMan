from spinnman.messages.scp.abstract_messages import AbstractSCPResponse
from spinnman.messages.scp.enums import SCPResult
from spinnman.exceptions import SpinnmanUnexpectedResponseCodeException
from spinn_utilities.overrides import overrides


class CheckOKResponse(AbstractSCPResponse):
    """ An SCP response to a request which returns nothing other than OK
    """
    __slots__ = [
        "_command",
        "_operation"]

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

    @overrides(AbstractSCPResponse.read_data_bytestring)
    def read_data_bytestring(self, data, offset):
        result = self.scp_response_header.result
        if result != SCPResult.RC_OK:
            raise SpinnmanUnexpectedResponseCodeException(
                self._operation, self._command, result.name)
