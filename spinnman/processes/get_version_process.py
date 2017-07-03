from spinnman.messages.scp.impl import GetVersion
from .abstract_single_connection_process import AbstractSingleConnectionProcess


class GetVersionProcess(AbstractSingleConnectionProcess):
    """ A process for getting the version of the machine
    """

    def __init__(self, connection_selector):
        AbstractSingleConnectionProcess.__init__(self, connection_selector)
        self._version_info = None

    def _get_response(self, version_response):
        self._version_info = version_response.version_info

    def get_version(self, x, y, p):
        self._send_request(GetVersion(x=x, y=y, p=p),
                           self._get_response)
        self._finish()

        self.check_for_error()
        return self._version_info
