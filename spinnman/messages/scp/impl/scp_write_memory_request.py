from spinnman.messages.scp.abstract_messages.abstract_scp_request\
    import AbstractSCPRequest
from spinnman.messages.sdp.sdp_header import SDPHeader
from spinnman.messages.sdp.sdp_flag import SDPFlag
from spinnman.messages.scp.scp_request_header import SCPRequestHeader
from spinnman.messages.scp.scp_command import SCPCommand
from spinnman.messages.scp.impl.scp_check_ok_response import SCPCheckOKResponse
from spinnman.messages.scp.impl.scp_utils import address_length_dtype


class SCPWriteMemoryRequest(AbstractSCPRequest):
    """ A request to write memory on a chip
    """

    def __init__(self, x, y, base_address, data, offset=0, length=None, cpu=0):
        """

        :param x: The x-coordinate of the chip, between 0 and 255
        :type x: int
        :param y: The y-coordinate of the chip, between 0 and 255
        :type y: int
        :param base_address: The base_address to start writing to
        :type base_address: int
        :param data: Up to 256 bytes of data to write
        :type data: bytearray
        """
        self._size = length
        self._offset = offset
        self._data_to_write = data
        if length is None:
            self._size = len(data)
        super(SCPWriteMemoryRequest, self).__init__(
            SDPHeader(
                flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                destination_cpu=cpu, destination_chip_x=x,
                destination_chip_y=y),
            SCPRequestHeader(command=SCPCommand.CMD_WRITE),
            argument_1=base_address, argument_2=self._size,
            argument_3=address_length_dtype[
                (base_address % 4), (self._size % 4)],
            data=None)

    @property
    def bytestring(self):
        datastring = super(SCPWriteMemoryRequest, self).bytestring
        data = self._data_to_write[self._offset:self._offset + self._size]
        return datastring + bytes(data)

    def get_scp_response(self):
        return SCPCheckOKResponse("WriteMemory", "CMD_WRITE")
