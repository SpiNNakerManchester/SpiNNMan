"""
ScpWriteFPGARegisterRequest
"""

# spinnman imports
import struct

from spinnman.messages.scp.abstract_messages import BMPRequest
from spinnman.messages.scp import SCPRequestHeader
from spinnman.messages.scp.enums import SCPCommand
from .check_ok_response import CheckOKResponse


class WriteFPGARegister(BMPRequest):
    """ A request for writing data to a FPGA register
    """

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

        BMPRequest.__init__(
            self, board,
            SCPRequestHeader(command=SCPCommand.CMD_LINK_WRITE),
            argument_1=addr & (~0x3), argument_2=4, argument_3=fpga_num,
            data=struct.pack("<I", value))

    def get_scp_response(self):
        """
        :rtype: spinnman.messages.scp.impl.CheckOKResponse
        """
        return CheckOKResponse("Send FPGA register write", "CMD_LINK_WRITE")
