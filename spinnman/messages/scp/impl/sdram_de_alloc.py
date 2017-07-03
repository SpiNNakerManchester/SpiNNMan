from spinnman.messages.scp import SCPRequestHeader
from spinnman.messages.scp.abstract_messages \
    import AbstractSCPRequest, AbstractSCPResponse
from spinnman.messages.scp.enums \
    import AllocFree, SCPCommand, SCPResult
from spinnman.messages.sdp import SDPFlag, SDPHeader
from spinnman.exceptions import SpinnmanUnexpectedResponseCodeException

import struct


class SDRAMDeAlloc(AbstractSCPRequest):
    """ An SCP Request to free space in the SDRAM
    """

    def __init__(self, x, y, app_id, base_address=None):
        """

        :param x: The x-coordinate of the chip to allocate on, between 0 and\
                    255
        :type x: int
        :param y: The y-coordinate of the chip to allocate on, between 0 and\
                    255
        :type y: int
        :param app_id: The id of the application, between 0 and 255
        :type app_id: int
        :param base_address: The start address in SDRAM to which the block\
                needs to be deallocated, or none if deallocating via app_id
        :type base_address: int or None
        """

        if base_address is not None:
            AbstractSCPRequest.__init__(
                self,
                SDPHeader(
                    flags=SDPFlag.REPLY_NOT_EXPECTED, destination_port=0,
                    destination_cpu=0, destination_chip_x=x,
                    destination_chip_y=y),
                SCPRequestHeader(command=SCPCommand.CMD_ALLOC),
                argument_1=(
                    app_id << 8 |
                    AllocFree.
                    FREE_SDRAM_BY_POINTER.value),  # @UndefinedVariable
                argument_2=base_address)
        else:
            AbstractSCPRequest.__init__(
                self,
                SDPHeader(
                    flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                    destination_cpu=0, destination_chip_x=x,
                    destination_chip_y=y),
                SCPRequestHeader(command=SCPCommand.CMD_ALLOC),
                argument_1=(
                    app_id << 8 |
                    AllocFree.
                    FREE_ROUTING_BY_APP_ID.value))  # @UndefinedVariable

    def get_scp_response(self):
        return _SCPSDRAMDeAllocResponse()


class _SCPSDRAMDeAllocResponse(AbstractSCPResponse):
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
