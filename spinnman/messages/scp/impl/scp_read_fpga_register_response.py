"""
SCPReadFPGARegisterResponse
"""
from spinnman.messages.scp.abstract_messages.abstract_scp_bmp_reponse import \
    AbstractSCPBMPResponse
from spinnman.messages.scp.scp_result import SCPResult
from spinnman.exceptions import SpinnmanUnexpectedResponseCodeException
from spinnman.model.version_info import VersionInfo

import struct

class SCPReadFPGARegisterResponse(AbstractSCPBMPResponse):
    """ An SCP response to a request for the version of software running
    """

    def __init__(self):
        """
        """
        AbstractSCPBMPResponse.__init__(self)
        self._fpga_register = None

    def read_scp_response(self, byte_reader):
        """ See :py:meth:`spinnman.messages.scp.abstract_scp_response.AbstractSCPResponse.read_scp_response`
        """
        AbstractSCPBMPResponse.read_scp_response(self, byte_reader)
        result = self.scp_response_header.result
        if result != SCPResult.RC_OK:
            raise SpinnmanUnexpectedResponseCodeException(
                "Read fpga register", "CMD_LINK_READ", result.name)
        data = byte_reader.read_bytes()
        self._fpga_register = struct.unpack("<I", data)[0]

    @property
    def fpga_register(self):
        """ The register information received

        :rtype: bytearray
        """
        return self._fpga_register

