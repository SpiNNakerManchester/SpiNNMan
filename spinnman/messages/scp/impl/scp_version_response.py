from spinnman.messages.scp.abstract_messages.abstract_scp_response import AbstractSCPResponse
from spinnman.messages.scp.scp_result import SCPResult
from spinnman.exceptions import SpinnmanUnexpectedResponseCodeException
from spinnman.model.version_info import VersionInfo


class SCPVersionResponse(AbstractSCPResponse):
    """ An SCP response to a request for the version of software running
    """

    def __init__(self):
        """
        """
        super(SCPVersionResponse, self).__init__()
        self._version_info = None

    def read_scp_response(self, byte_reader):
        """ See :py:meth:`spinnman.messages.scp.abstract_scp_response.AbstractSCPResponse.read_scp_response`
        """
        super(SCPVersionResponse, self).read_scp_response(byte_reader)
        result = self.scp_response_header.result
        if result != SCPResult.RC_OK:
            raise SpinnmanUnexpectedResponseCodeException(
                "Version", "CMD_VER", result.name)
        data = byte_reader.read_bytes()
        self._version_info = VersionInfo(data)

    @property
    def version_info(self):
        """ The version information received

        :rtype: :py:class:`spinnman.model.version_info.VersionInfo`
        """
        return self._version_info
