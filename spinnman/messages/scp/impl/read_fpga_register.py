# spinnman imports
from spinnman.messages.scp.abstract_messages \
    import BMPRequest, BMPResponse
from spinnman.messages.scp.enums import SCPCommand, SCPResult
from spinnman.messages.scp import SCPRequestHeader
from spinnman.exceptions import SpinnmanUnexpectedResponseCodeException

import struct

_ONE_WORD = struct.Struct("<I")


class ReadFPGARegister(BMPRequest):
    """ Requests the data from a FPGA's register
    """
    __slots__ = []

    def __init__(self, fpga_num, register, board):
        """ Sets up a read FPGA register request.

        :param fpga_num: FPGA number (0, 1 or 2) to communicate with.
        :param register: Register address to read to (will be rounded down to\
            the nearest 32-bit word boundary).
        :param board: which board to request the FPGA register from
        :rtype: None
        """

        # check to stop people asking for none word aligned memory addresses
        # inverses all bits of a value, so is basically a inverse mask for the
        # value entered.
        arg1 = register & (~0x3)
        super(ReadFPGARegister, self).__init__(
            board,
            SCPRequestHeader(command=SCPCommand.CMD_LINK_READ),
            argument_1=arg1, argument_2=4, argument_3=fpga_num)

    def get_scp_response(self):
        return _SCPReadFPGARegisterResponse()


class _SCPReadFPGARegisterResponse(BMPResponse):
    """ An SCP response to a request for the version of software running
    """
    __slots__ = [
        "_fpga_register"]

    def __init__(self):
        super(_SCPReadFPGARegisterResponse, self).__init__()
        self._fpga_register = None

    def read_data_bytestring(self, data, offset):
        """ See\
            :py:meth:`spinnman.messages.scp.abstract_scp_response.AbstractSCPResponse.read_data_bytestring`
        """
        result = self.scp_response_header.result
        if result != SCPResult.RC_OK:
            raise SpinnmanUnexpectedResponseCodeException(
                "Read FPGA register", "CMD_LINK_READ", result.name)

        self._fpga_register = _ONE_WORD.unpack_from(data, offset)[0]

    @property
    def fpga_register(self):
        """ The register information received

        :rtype: int
        """
        return self._fpga_register
