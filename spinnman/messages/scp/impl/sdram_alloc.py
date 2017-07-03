from spinnman.messages.scp import SCPRequestHeader
from spinnman.messages.scp.abstract_messages \
    import AbstractSCPRequest, AbstractSCPResponse
from spinnman.messages.scp.enums \
    import SCPAllocFreeType, SCPCommand, SCPResult
from spinnman.messages.sdp import SDPFlag, SDPHeader
from spinnman.exceptions import SpinnmanUnexpectedResponseCodeException
from spinnman.exceptions import SpinnmanInvalidParameterException

import struct


class SCPSDRAMAllocRequest(AbstractSCPRequest):
    """ An SCP Request to allocate space in the SDRAM space
    """

    def __init__(self, x, y, app_id, size, tag=None):
        """

        :param x: The x-coordinate of the chip to allocate on, between 0 and\
                    255
        :type x: int
        :param y: The y-coordinate of the chip to allocate on, between 0 and\
                    255
        :type y: int
        :param app_id: The id of the application, between 0 and 255
        :type app_id: int
        :param size: The size in bytes of memory to be allocated
        :type size: int
        :param tag: the tag for the SDRAM, a 8-bit (chip-wide) tag that can be\
                looked up by a SpiNNaker application to discover the address\
                of the allocated block. If `0` then no tag is applied.
        :type tag: int
        """

        if tag is None:
            tag = 0
        elif not(0 <= tag < 256):
            raise SpinnmanInvalidParameterException(
                "tag",
                "The tag param needs to be between 0 and 255, or None (in "
                "which case 0 will be used by default)", str(tag))

        AbstractSCPRequest.__init__(
            self,
            SDPHeader(
                flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                destination_cpu=0, destination_chip_x=x,
                destination_chip_y=y),
            SCPRequestHeader(command=SCPCommand.CMD_ALLOC),
            argument_1=(
                (app_id << 8) |
                SCPAllocFreeType.ALLOC_SDRAM.value),  # @UndefinedVariable
            argument_2=size, argument_3=tag)
        self._size = size

    def get_scp_response(self):
        return _SCPSDRAMAllocResponse(self._size)


class _SCPSDRAMAllocResponse(AbstractSCPResponse):
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