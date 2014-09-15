from spinnman.messages.scp.abstract_messages.abstract_scp_request import AbstractSCPRequest
from spinnman.exceptions import SpinnmanInvalidParameterException
from spinnman.messages.sdp.sdp_header import SDPHeader
from spinnman.messages.sdp.sdp_flag import SDPFlag
from spinnman.messages.scp.scp_request_header import SCPRequestHeader
from spinnman.messages.scp.scp_command import SCPCommand
from spinnman.messages.scp.impl.scp_check_ok_response import SCPCheckOKResponse


class SCPWriteLinkRequest(AbstractSCPRequest):
    """ A request to write memory on a neighbouring chip
    """

    def __init__(self, x, y, cpu, link, base_address, data):
        """

        :param x: The x-coordinate of the chip whose neighbour will be written \
                    to, between 0 and 255
        :type x: int
        :param y: The y-coordinate of the chip whose neighbour will be written \
                    to, between 0 and 255
        :type y: int
        :param cpu: The CPU core to use, normally 0 (or if a BMP, the board \
                      slot number)
        :type cpu: int
        :param link: The link number to write to between 0 and 5 (or if a BMP, \
                       the FPGA between 0 and 2)
        :type link: int
        :param base_address: The base_address to start writing to
        :type base_address: int
        :param data: Up to 256 bytes of data to write
        :type data: bytearray
        :raise spinnman.exceptions.SpinnmanInvalidParameterException:\
                    * If x is out of range
                    * If y is out of range
                    * If base_address is not positive
                    * If the length of data is 0 or more than 256
        """

        if base_address < 0:
            raise SpinnmanInvalidParameterException(
                "base_address", str(base_address),
                "Must be a positive integer")
        if len(data) == 0:
            raise SpinnmanInvalidParameterException(
                "len(data)", str(len(data)), "Must be something to write")
        if len(data) > 256:
            raise SpinnmanInvalidParameterException(
                "len(data)", str(len(data)),
                "Must be less than 256 bytes")

        super(SCPWriteLinkRequest, self).__init__(
            SDPHeader(
                flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                destination_cpu=cpu, destination_chip_x=x,
                destination_chip_y=y),
            SCPRequestHeader(command=SCPCommand.CMD_LINK_WRITE),
            argument_1=base_address, argument_2=len(data), argument_3=link,
            data=data)

    def get_scp_response(self):
        return SCPCheckOKResponse("WriteMemory", "CMD_WRITE")
