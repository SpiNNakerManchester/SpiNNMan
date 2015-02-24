from spinnman.messages.scp.abstract_messages.abstract_scp_response \
    import AbstractSCPResponse
from spinnman.messages.scp.scp_result import SCPResult
from spinnman.exceptions import SpinnmanUnexpectedResponseCodeException


class SCPReadMemoryWordsResponse(AbstractSCPResponse):
    """ An SCP response to a request to read a region of memory on a chip\
        in words
    """

    def __init__(self):
        """
        """
        super(SCPReadMemoryWordsResponse, self).__init__()
        self._data = None

    def read_scp_response(self, byte_reader):
        """ See\
            :py:meth:`spinnman.messages.scp.abstract_scp_response.AbstractSCPResponse.read_scp_response`
        """
        super(SCPReadMemoryWordsResponse, self).read_scp_response(byte_reader)
        result = self.scp_response_header.result
        if result != SCPResult.RC_OK:
            raise SpinnmanUnexpectedResponseCodeException(
                "Read", "CMD_READ", result.name)
        self._data = list()
        while not byte_reader.is_at_end():
            self._data.append(byte_reader.read_int())

    @property
    def data(self):
        """ The words of data read

        :rtype: array-like of int
        """
        return self._data
