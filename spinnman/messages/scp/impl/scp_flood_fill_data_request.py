from spinnman.messages.scp.abstract_messages.abstract_scp_request import AbstractSCPRequest
from spinnman.exceptions import SpinnmanInvalidParameterException
from spinnman.messages.sdp.sdp_header import SDPHeader
from spinnman.messages.sdp.sdp_flag import SDPFlag
from spinnman.messages.scp.scp_request_header import SCPRequestHeader
from spinnman.messages.scp.scp_command import SCPCommand
from spinnman.messages.scp.impl.scp_check_ok_response import SCPCheckOKResponse

_NNP_FORWARD_RETRY = (0x3f << 24) | (0x18 << 16)
_NNP_FLOOD_FILL_START = 6


class SCPFloodFillDataRequest(AbstractSCPRequest):
    """ A request to start a flood fill of data
    """

    def __init__(self, nearest_neighbour_id, block_no, base_address, data):
        """

        :param nearest_neighbour_id: The id of the packet, between 0 and 127
        :type nearest_neighbour_id: int
        :param block_no: Which block this block is, between 0 and 255
        :type block_no: int
        :param base_address: The base address where the data is to be loaded
        :type base_address: int
        :param data: The data to load, between 4 and 256 bytes and the size\
                    must be divisible by 4
        :type data: bytearray
        :raise spinnman.exceptions.SpinnmanInvalidParameterException:
                    * If the id is out of range
                    * If the block number is out of range
                    * If the base_address is not a positive integer
                    * If the data is too long or too short
                    * If the length of the data is not divisible by 4
        """
        if nearest_neighbour_id < 0 or nearest_neighbour_id > 127:
            raise SpinnmanInvalidParameterException(
                    "nearest_neighbour_id", nearest_neighbour_id,
                    "Must be between 0 and 127")
        if block_no < 0 or block_no > 255:
            raise SpinnmanInvalidParameterException(
                    "block_no", block_no, "Must be between 0 and 255")
        if base_address < 0:
            raise SpinnmanInvalidParameterException(
                    "base_address", base_address, "Must be a positive integer")
        if len(data) < 1:
            raise SpinnmanInvalidParameterException(
                    "len(data)", len(data), "Must be at least 1 byte of data")
        if len(data) > 256:
            raise SpinnmanInvalidParameterException(
                    "len(data)", len(data), "Must be less than 256 bytes")
        if len(data) % 4 != 0:
            raise SpinnmanInvalidParameterException(
                    "len(data)", len(data), "Must be divisible by 4")

        argument_1 = _NNP_FORWARD_RETRY | nearest_neighbour_id
        argument_2 = (block_no << 16) | (((len(data) / 4) - 1) << 8)

        super(SCPFloodFillDataRequest, self).__init__(
                SDPHeader(flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                        destination_cpu=0, destination_chip_x=0,
                        destination_chip_y=0),
                SCPRequestHeader(command=SCPCommand.CMD_FFD),
                argument_1=argument_1, argument_2=argument_2,
                argument_3=base_address, data=data)

    def get_scp_response(self):
        return SCPCheckOKResponse("Flood Fill", "CMD_NNP:NNP_FFS")
