from spinnman.messages.scp import SCPRequestHeader
from spinnman.messages.scp.abstract_messages import AbstractSCPRequest
from spinnman.messages.scp.enums import SCPAllocFreeType, SCPCommand
from spinnman.messages.sdp import SDPFlag, SDPHeader
from .scp_router_alloc_response import SCPRouterAllocResponse


class SCPRouterAllocRequest(AbstractSCPRequest):
    """ An SCP Request to allocate space for routing entries
    """

    def __init__(self, x, y, app_id, n_entries):
        """

        :param x: The x-coordinate of the chip to allocate on, between 0 and\
                    255
        :type x: int
        :param y: The y-coordinate of the chip to allocate on, between 0 and\
                    255
        :type y: int
        :param app_id: The id of the application, between 0 and 255
        :type app_id: int
        :param n_entries: The number of entries to allocate
        :type n_entries: int
        """
        super(SCPRouterAllocRequest, self).__init__(
            SDPHeader(
                flags=SDPFlag.REPLY_EXPECTED, port=0,
                destination_cpu=0, destination_chip_x=x,
                destination_chip_y=y),
            SCPRequestHeader(command=SCPCommand.CMD_ALLOC),
            argument_1=(
                (app_id << 8) |
                SCPAllocFreeType.ALLOC_ROUTING.value),  # @UndefinedVariable
            argument_2=n_entries)

    def get_scp_response(self):
        return SCPRouterAllocResponse()
