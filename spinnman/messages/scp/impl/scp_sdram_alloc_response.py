import struct

from spinnman.messages.scp.abstract_messages.abstract_scp_response\
    import AbstractSCPResponse
from spinnman.messages.scp.enums.scp_result import SCPResult
from spinnman.exceptions import SpinnmanUnexpectedResponseCodeException
from spinnman.exceptions import SpinnmanInvalidParameterException


class SCPSDRAMAllocResponse(AbstractSCPResponse):
    """ An SCP response to a request to allocate space in SDRAM
    """

    def __init__(self, size):
        """
        """
        AbstractSCPResponse.__init__(self)
        self._size = size
        self._base_address = None

    def read_data_bytestring(self, data, offset):
        """ See\
            :py:meth:`spinnman.messages.scp.abstract_scp_response.AbstractSCPResponse.read_data_bytestring`
        """
        result = self.scp_response_header.result
        if result != SCPResult.RC_OK:
            raise SpinnmanUnexpectedResponseCodeException(
                "SDRAM Allocation", "CMD_ALLOC", result.name)
        self._base_address = struct.unpack_from("<I", data, offset)[0]

        # check that the base address is not null (0 in python case) as
        # this reflects a issue in the command on spinnaker side
        if self._base_address == 0:
            raise SpinnmanInvalidParameterException(
                "SDRAM Allocation response base address", self._base_address,
                "Could not allocate {} bytes of SDRAM".format(self._size))

    @property
    def base_address(self):
        """ The base address allocated, or 0 if none

        :rtype: int
        """
        return self._base_address
