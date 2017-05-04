import struct

from spinnman.messages.scp.abstract_messages.abstract_scp_response\
    import AbstractSCPResponse
from spinnman.messages.scp.enums.scp_result import SCPResult
from spinnman.exceptions import SpinnmanUnexpectedResponseCodeException


class SCPSDRAMDeAllocResponse(AbstractSCPResponse):
    """ An SCP response to a request to deallocate SDRAM
    """

    def __init__(self, read_n_blocks_freed=False):
        """
        """
        AbstractSCPResponse.__init__(self)
        self._number_of_blocks_freed = None
        self._read_n_blocks_freed = read_n_blocks_freed

    def read_data_bytestring(self, data, offset):
        """ See\
            :py:meth:`spinnman.messages.scp.abstract_scp_response.AbstractSCPResponse.read_data_bytestring`
        """
        result = self.scp_response_header.result
        if result != SCPResult.RC_OK:
            raise SpinnmanUnexpectedResponseCodeException(
                "SDRAM deallocation", "CMD_DEALLOC", result.name)
        if self._read_n_blocks_freed:
            self._number_of_blocks_freed = struct.unpack_from(
                "<I", data, offset)[0]

    @property
    def number_of_blocks_freed(self):
        """ The number of allocated blocks that have been freed from the\
            app_id given

        :rtype: int
        """
        return self._number_of_blocks_freed
