from spinnman.messages.scp.abstract_messages.abstract_scp_request\
    import AbstractSCPRequest
from spinnman.messages.sdp.sdp_header import SDPHeader
from spinnman.messages.sdp.sdp_flag import SDPFlag
from spinnman.messages.scp.scp_request_header import SCPRequestHeader
from spinnman.messages.scp.enums.scp_command import SCPCommand
from spinnman.messages.scp.impl.scp_check_ok_response import SCPCheckOKResponse


class SCPWriteLinkRequest(AbstractSCPRequest):
    """ A request to write memory on a neighbouring chip
    """

    def __init__(self, x, y, link, base_address, data, cpu=0):
        """

        :param x: The x-coordinate of the chip whose neighbour will be written\
                    to, between 0 and 255
        :type x: int
        :param y: The y-coordinate of the chip whose neighbour will be written\
                    to, between 0 and 255
        :type y: int
        :param cpu: The CPU core to use, normally 0 (or if a BMP, the board \
                      slot number)
        :type cpu: int
        :param link: The link number to write to between 0 and 5 (or if a BMP,\
                       the FPGA between 0 and 2)
        :type link: int
        :param base_address: The base_address to start writing to
        :type base_address: int
        :param data: Up to 256 bytes of data to write
        :type data: bytearray
        """
        super(SCPWriteLinkRequest, self).__init__(
            SDPHeader(
                flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                destination_cpu=cpu, destination_chip_x=x,
                destination_chip_y=y),
            SCPRequestHeader(command=SCPCommand.CMD_LINK_WRITE),
            argument_1=base_address, argument_2=len(data), argument_3=link,
            data=None)
        self._data_to_write = data

    @property
    def bytestring(self):
        datastring = super(SCPWriteLinkRequest, self).bytestring
        return datastring + bytes(self._data_to_write)

    def get_scp_response(self):
        return SCPCheckOKResponse("WriteMemory", "CMD_WRITE")
