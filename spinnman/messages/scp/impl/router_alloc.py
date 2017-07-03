from spinnman.messages.scp import SCPRequestHeader
from spinnman.messages.scp.abstract_messages \
    import AbstractSCPRequest, AbstractSCPResponse
from spinnman.messages.scp.enums \
    import AllocFree, SCPCommand, SCPResult
from spinnman.messages.sdp import SDPFlag, SDPHeader
from spinnman.exceptions import SpinnmanUnexpectedResponseCodeException

import struct


class RouterAlloc(AbstractSCPRequest):
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
        super(RouterAlloc, self).__init__(
            SDPHeader(
                flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                destination_cpu=0, destination_chip_x=x,
                destination_chip_y=y),
            SCPRequestHeader(command=SCPCommand.CMD_ALLOC),
            argument_1=(
                (app_id << 8) |
                AllocFree.ALLOC_ROUTING.value),  # @UndefinedVariable
            argument_2=n_entries)

    def get_scp_response(self):
        return _SCPRouterAllocResponse()


class _SCPRouterAllocResponse(AbstractSCPResponse):
    """ An SCP response to a request to allocate router entries
    """

    def __init__(self):
        """
        """
        super(_SCPRouterAllocResponse, self).__init__()
        self._base_address = None

    def read_data_bytestring(self, data, offset):
        """ See\
            :py:meth:`spinnman.messages.scp.abstract_scp_response.AbstractSCPResponse.read_data_bytestring`
        """
        result = self.scp_response_header.result
        if result != SCPResult.RC_OK:
            raise SpinnmanUnexpectedResponseCodeException(
                "Router Allocation", "CMD_ALLOC", result.name)
        self._base_address = struct.unpack_from("<I", data, offset)[0]

    @property
    def base_address(self):
        """ The base address allocated, or 0 if none

        :rtype: int
        """
        return self._base_address
