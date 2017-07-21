import struct

from spinnman.messages.scp.abstract_messages import AbstractSCPResponse
from spinnman.messages.scp.enums import SCPResult
from spinnman.exceptions import SpinnmanUnexpectedResponseCodeException


class IPTagGetInfoResponse(AbstractSCPResponse):
    """ An SCP response to a request for information about IP tags
    """

    def __init__(self):
        """
        """
        super(IPTagGetInfoResponse, self).__init__()
        self._tto = None
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

        self._tto, self._pool_size, self._fixed_size = struct.unpack_from(
            "<Bx2B", data, offset)

    @property
    def transient_timeout(self):
        """ The timeout for transient IP tags (i.e. responses to SCP commands)

        :rtype: int
        """
        return self._tto

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
