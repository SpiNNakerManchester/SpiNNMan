from spinnman.messages.scp.abstract_messages.abstract_scp_response\
    import AbstractSCPResponse
from spinnman.messages.scp.scp_result import SCPResult
from spinnman.exceptions import SpinnmanUnexpectedResponseCodeException
import struct


class SCPIPTagInfoResponse(AbstractSCPResponse):
    """ An SCP response to a request for information about IP tags
    """

    def __init__(self):
        """
        """
        super(SCPIPTagInfoResponse, self).__init__()
        self._pool_size = None
        self._fixed_size = None

    def read_data_bytestring(self, data, offset):
        """ See\
            :py:meth:`spinnman.messages.scp.abstract_scp_response.AbstractSCPResponse.read_data_bytestring`
        """
        result = self.scp_response_header.result
        if result != SCPResult.RC_OK:
            raise SpinnmanUnexpectedResponseCodeException(
                "Get IP Tag Info", "CMD_IPTAG", result.name)

        self._pool_size, self._fixed_size = struct.unpack_from(
            "<2x2B", data, offset)

    @property
    def pool_size(self):
        """ The count of the IP tag pool size

        :rtype: int
        """
        return self._pool_size

    @property
    def fixed_size(self):
        """ The count of the number of fixed IP tag entries

        :rtype: int
        """
        return self._fixed_size
