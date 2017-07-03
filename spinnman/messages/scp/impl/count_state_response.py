import struct

from spinnman.messages.scp.abstract_messages import AbstractSCPResponse
from spinnman.messages.scp.enums import SCPResult
from spinnman.exceptions import SpinnmanUnexpectedResponseCodeException


class CountStateResponse(AbstractSCPResponse):
    """ An SCP response to a request for the number of cores in a given state
    """

    def __init__(self):
        """
        """
        super(CountStateResponse, self).__init__()
        self._count = None

    def read_data_bytestring(self, data, offset):
        """ See\
            :py:meth:`spinnman.messages.scp.abstract_scp_response.AbstractSCPResponse.read_data_bytestring`
        """
        result = self.scp_response_header.result
        if result != SCPResult.RC_OK:
            raise SpinnmanUnexpectedResponseCodeException(
                "CountState", "CMD_SIGNAL", result.name)
        self._count = struct.unpack_from("<I", data, offset)[0]

    @property
    def count(self):
        """ The count of the number of cores with the requested state

        :rtype: int
        """
        return self._count
