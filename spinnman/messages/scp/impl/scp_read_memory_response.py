from spinnman.messages.scp.abstract_messages.abstract_scp_response import AbstractSCPResponse
from spinnman.messages.scp.scp_result import SCPResult
from spinnman.exceptions import SpinnmanUnexpectedResponseCodeException


class SCPReadMemoryResponse(AbstractSCPResponse):
    """ An SCP response to a request to read a region of memory on a chip
    """

    def __init__(self):
        """
        """
        super(SCPReadMemoryResponse, self).__init__()
        self._data = None

    def read_scp_response(self, byte_reader):
        """ See :py:meth:`spinnman.messages.scp.abstract_scp_response.AbstractSCPResponse.read_scp_response`
        """
        super(SCPReadMemoryResponse, self).read_scp_response(byte_reader)
        result = self.scp_response_header.result
        if result != SCPResult.RC_OK:
            raise SpinnmanUnexpectedResponseCodeException(
                "Read", "CMD_READ", result.name)
        self._data = byte_reader.read_bytes()

    @property
    def data(self):
        """ The data read

        :rtype: bytearray
        """
        return self._data
