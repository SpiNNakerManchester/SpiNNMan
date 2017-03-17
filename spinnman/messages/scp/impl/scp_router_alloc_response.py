import struct

from spinnman.messages.scp.abstract_messages.abstract_scp_response\
    import AbstractSCPResponse
from spinnman.messages.scp.enums.scp_result import SCPResult
from spinnman.exceptions import SpinnmanUnexpectedResponseCodeException


class SCPRouterAllocResponse(AbstractSCPResponse):
    """ An SCP response to a request to allocate router entries
    """

    def __init__(self):
        """
        """
        super(SCPRouterAllocResponse, self).__init__()
        self._base_address = None

    def read_data_bytestring(self, data, offset):
        """ See\
            :py:meth:`spinnman.messages.scp.abstract_scp_response.AbstractSCPResponse.read_data_bytestring`
        """
        result = self.scp_response_header.result
        if result != SCPResult.RC_OK:
            raise SpinnmanUnexpectedResponseCodeException(
                "Router Allocation", "CMD_ALLOC", result.name)
        self._base_address = struct.unpack_from("<I", data, offset)[0]

    @property
    def base_address(self):
        """ The base address allocated, or 0 if none

        :rtype: int
        """
        return self._base_address
