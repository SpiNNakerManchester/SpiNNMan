from spinnman import exceptions

from spinnman.messages.scp.abstract_messages.abstract_scp_request\
    import AbstractSCPRequest
from spinnman.messages.scp.impl.scp_sdram_alloc_response import \
    SCPSDRAMAllocResponse
from spinnman.messages.sdp.sdp_header import SDPHeader
from spinnman.messages.sdp.sdp_flag import SDPFlag
from spinnman.messages.scp.scp_request_header import SCPRequestHeader
from spinnman.messages.scp.enums.scp_command import SCPCommand
from spinnman.messages.scp.enums.scp_alloc_free_type import SCPAllocFreeType


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
            raise exceptions.SpinnmanInvalidParameterException(
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
        return SCPSDRAMAllocResponse(self._size)
