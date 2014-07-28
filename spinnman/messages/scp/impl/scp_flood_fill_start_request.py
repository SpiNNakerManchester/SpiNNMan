from spinnman.messages.scp.abstract_messages.abstract_scp_request import AbstractSCPRequest
from spinnman.exceptions import SpinnmanInvalidParameterException
from spinnman.messages.sdp.sdp_header import SDPHeader
from spinnman.messages.sdp.sdp_flag import SDPFlag
from spinnman.messages.scp.scp_request_header import SCPRequestHeader
from spinnman.messages.scp.scp_command import SCPCommand
from spinnman.messages.scp.impl.scp_check_ok_response import SCPCheckOKResponse

_NNP_FORWARD_RETRY = (1 << 31) | (0x3f << 8) | 0x18
_NNP_FLOOD_FILL_START = 6


class SCPFloodFillStartRequest(AbstractSCPRequest):
    """ A request to start a flood fill of data
    """

    def __init__(self, nearest_neighbour_id, n_blocks, x=None, y=None):
        """

        :param nearest_neighbour_id: The id of the packet, between 0 and 127
        :type nearest_neighbour_id: int
        :param n_blocks: The number of blocks of data that will be sent,\
                    between 0 and 255
        :type n_blocks: int
        :param x: The x-coordindate of the chip to load the data on to.  If\
                    not specified, the data will be loaded on to all chips
        :type x: int
        :param y: The y-coordinate of the chip to load the data on to.  If\
                    not specified, the data will be loaded on to all chips
        :type y: int
        :raise spinnman.exceptions.SpinnmanInvalidParameterException:
                    * If the id is out of range
                    * If the number of blocks is out of range
                    * If only one of x or y is specified
                    * If x and y are out of range
        """
        if nearest_neighbour_id < 0 or nearest_neighbour_id > 127:
            raise SpinnmanInvalidParameterException(
                    "nearest_neighbour_id", str(nearest_neighbour_id),
                    "Must be between 0 and 127")
        if n_blocks < 0 or n_blocks > 255:
            raise SpinnmanInvalidParameterException(
                    "n_blocks", str(n_blocks), "Must be between 0 and 255")
        if (x is None and y is not None) or (x is not None and y is None):
            raise SpinnmanInvalidParameterException(
                    "x and y", "{} and {}".format(x, y),
                    "Both or neither of x and y must be specified")
        if x is not None and (x < 0 or x > 255):
            raise SpinnmanInvalidParameterException(
                    "x", str(x), "Must be between 0 and 255")
        if y is not None and (y < 0 or y > 255):
            raise SpinnmanInvalidParameterException(
                    "y", str(y), "Must be between 0 and 255")

        key = ((_NNP_FLOOD_FILL_START << 24) | (nearest_neighbour_id << 16)
                | (n_blocks << 8))
        data = 0xFFFF
        if x is not None and y is not None:
            m = ((y & 3) * 4) + (x & 3)
            data = (((x & 0xfc) << 24) + ((y & 0xfc) << 16)
                    + (3 << 16) + (1 << m))

        super(SCPFloodFillStartRequest, self).__init__(
                SDPHeader(flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                        destination_cpu=0, destination_chip_x=0,
                        destination_chip_y=0),
                SCPRequestHeader(command=SCPCommand.CMD_NNP),
                argument_1=key, argument_2=data, argument_3=_NNP_FORWARD_RETRY)

    def get_scp_response(self):
        return SCPCheckOKResponse("Flood Fill", "CMD_NNP:NNP_FFS")
