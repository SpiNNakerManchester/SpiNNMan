"""
SCPReadFPGARegisterResponse
"""
import struct

from spinnman.messages.scp.abstract_messages.abstract_scp_bmp_reponse import \
    AbstractSCPBMPResponse
from spinnman.messages.scp.enums.scp_result import SCPResult
from spinnman.exceptions import SpinnmanUnexpectedResponseCodeException


class SCPReadFPGARegisterResponse(AbstractSCPBMPResponse):
    """ An SCP response to a request for the version of software running
    """

    def __init__(self):
        """
        """
        AbstractSCPBMPResponse.__init__(self)
        self._fpga_register = None

    def read_data_bytestring(self, data, offset):
        """ See\
            :py:meth:`spinnman.messages.scp.abstract_scp_response.AbstractSCPResponse.read_data_bytestring`
        """
        result = self.scp_response_header.result
        if result != SCPResult.RC_OK:
            raise SpinnmanUnexpectedResponseCodeException(
                "Read FPGA register", "CMD_LINK_READ", result.name)

        self._fpga_register = struct.unpack_from("<I", data, offset)[0]

    @property
    def fpga_register(self):
        """ The register information received

        :rtype: int
        """
        return self._fpga_register
