from spinnman.messages.scp.abstract_messages.abstract_scp_response \
    import AbstractSCPResponse
from spinnman.messages.scp.enums.scp_result import SCPResult
from spinnman.exceptions import SpinnmanUnexpectedResponseCodeException


class SCPReadMemoryResponse(AbstractSCPResponse):
    """ An SCP response to a request to read a region of memory on a chip
    """

    def __init__(self):
        """
        """
        super(SCPReadMemoryResponse, self).__init__()
        self._data = None
        self._offset = None

    def read_data_bytestring(self, data, offset):
        if self._scp_response_header.result != SCPResult.RC_OK:
            raise SpinnmanUnexpectedResponseCodeException(
                "Read", "CMD_READ", self._scp_response_header.result)
        self._data = data
        self._offset = offset
        self._length = len(data) - offset

    @property
    def data(self):
        """ The data read - note that the data starts at offset

        :rtype: bytearray
        """
        return self._data

    @property
    def offset(self):
        """ The offset where the valid data starts

        :rtype: int
        """
        return self._offset

    @property
    def length(self):
        """ The length of the valid data

        :rtype: int
        """
        return self._length
