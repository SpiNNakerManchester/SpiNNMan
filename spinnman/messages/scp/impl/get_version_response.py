from spinnman.messages.scp.abstract_messages import AbstractSCPResponse
from spinnman.messages.scp.enums import SCPResult
from spinnman.exceptions import SpinnmanUnexpectedResponseCodeException
from spinnman.model import VersionInfo
from spinn_utilities import overrides


class GetVersionResponse(AbstractSCPResponse):
    """ An SCP response to a request for the version of software running
    """
    __slots__ = [
        "_version_info"]

    def __init__(self):
        super(GetVersionResponse, self).__init__()
        self._version_info = None

    @overrides(AbstractSCPResponse.read_data_bytestring)
    def read_data_bytestring(self, data, offset):
        result = self.scp_response_header.result
        if result != SCPResult.RC_OK:
            raise SpinnmanUnexpectedResponseCodeException(
                "Version", "CMD_VER", result.name)
        self._version_info = VersionInfo(data, offset)

    @property
    def version_info(self):
        """ The version information received

        :rtype: :py:class:`spinnman.model.version_info.VersionInfo`
        """
        return self._version_info
