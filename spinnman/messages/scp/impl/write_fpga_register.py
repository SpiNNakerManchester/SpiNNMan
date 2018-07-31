# spinnman imports
import struct

from spinnman.messages.scp.abstract_messages \
    import AbstractSCPRequest, BMPRequest
from spinnman.messages.scp import SCPRequestHeader
from spinnman.messages.scp.enums import SCPCommand
from .check_ok_response import CheckOKResponse
from spinn_utilities.overrides import overrides

_ONE_WORD = struct.Struct("<I")


class WriteFPGARegister(BMPRequest):
    """ A request for writing data to a FPGA register
    """
    __slots__ = []

    def __init__(self, fpga_num, addr, value, board):
        """ Write the value of an FPGA (SPI) register.

        See the SpI/O project's spinnaker_fpga design's `README`_ for a listing
        of FPGA registers. The SpI/O project can be found on GitHub at:
        https://github.com/SpiNNakerManchester/spio/

        .. _README: https://github.com/SpiNNakerManchester/spio/\
                    blob/master/designs/spinnaker_fpgas/README.md#spi-interface

        :param fpga_num: FPGA number (0, 1 or 2) to communicate with.
        :type fpga_num: int
        :param addr: Register address to read or write to (will be rounded
            down to the nearest 32-bit word boundary).
        :type addr: int
        :param value: A 32-bit int value to write to the register
        :type value: int
        """

        super(WriteFPGARegister, self).__init__(
            board,
            SCPRequestHeader(command=SCPCommand.CMD_LINK_WRITE),
            argument_1=addr & (~0x3), argument_2=4, argument_3=fpga_num,
            data=_ONE_WORD.pack(value))

    @overrides(AbstractSCPRequest.get_scp_response)
    def get_scp_response(self):
        return CheckOKResponse("Send FPGA register write", "CMD_LINK_WRITE")
