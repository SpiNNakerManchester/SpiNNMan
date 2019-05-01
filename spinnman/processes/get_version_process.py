from spinnman.messages.scp.impl import GetVersion
from .abstract_single_connection_process import AbstractSingleConnectionProcess
from spinnman.constants import N_RETRIES


class GetVersionProcess(AbstractSingleConnectionProcess):
    """ A process for getting the version of the machine.
    """
    __slots__ = [
        "_version_info"]

    def __init__(self, connection_selector, n_retries=N_RETRIES):
        super(GetVersionProcess, self).__init__(connection_selector, n_retries)
        self._version_info = None

    def _get_response(self, version_response):
        self._version_info = version_response.version_info

    def get_version(self, x, y, p):
        self._send_request(GetVersion(x=x, y=y, p=p),
                           self._get_response)
        self._finish()

        self.check_for_error()
        return self._version_info
