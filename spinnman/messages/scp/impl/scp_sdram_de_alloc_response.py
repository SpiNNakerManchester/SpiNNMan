import struct

from spinnman.messages.scp.abstract_messages.abstract_scp_response\
    import AbstractSCPResponse
from spinnman.messages.scp.enums.scp_result import SCPResult
from spinnman.exceptions import SpinnmanUnexpectedResponseCodeException


class SCPSDRAMDeAllocResponse(AbstractSCPResponse):
    """ An SCP response to a request to deallocate SDRAM
    """

    def __init__(self):
        """
        """
        AbstractSCPResponse.__init__(self)
        self._number_of_blocks_freed = None

    def read_data_bytestring(self, data, offset):
        """ See\
            :py:meth:`spinnman.messages.scp.abstract_scp_response.AbstractSCPResponse.read_data_bytestring`
        """
        result = self.scp_response_header.result
        if result != SCPResult.RC_OK:
            raise SpinnmanUnexpectedResponseCodeException(
                "SDRAM deallocation", "CMD_DEALLOC", result.name)
        self._number_of_blocks_freed = struct.unpack_from(
            "<I", data, offset)[0]

        # check that the base address is not null (0 in python case) as
        # this reflects a issue in command on spinnaker side
        if self._number_of_blocks_freed == 0:
            raise SpinnmanUnexpectedResponseCodeException(
                "SDRAM deallocation response base address", "CMD_DEALLOC",
                result.name)

    @property
    def number_of_blocks_freed(self):
        """ The number of allocated blocks that have been freed from the\
            app_id given

        :rtype: int
        """
        return self._number_of_blocks_freed
