from spinnman.messages.scp.abstract_messages.abstract_scp_request\
    import AbstractSCPRequest
from spinnman.messages.scp.impl.scp_sdram_de_alloc_response import \
    SCPSDRAMDeAllocResponse
from spinnman.messages.sdp.sdp_header import SDPHeader
from spinnman.messages.sdp.sdp_flag import SDPFlag
from spinnman.messages.scp.scp_request_header import SCPRequestHeader
from spinnman.messages.scp.enums.scp_command import SCPCommand
from spinnman.messages.scp.enums.scp_alloc_free_type import SCPAllocFreeType


class SCPSDRAMDeAllocRequest(AbstractSCPRequest):
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
                    SCPAllocFreeType.
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
                    SCPAllocFreeType.
                    FREE_ROUTING_BY_APP_ID.value))  # @UndefinedVariable

    def get_scp_response(self):
        return SCPSDRAMDeAllocResponse()
