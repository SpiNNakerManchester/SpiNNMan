from spinnman.connections.scp_request_set import SCPRequestSet
from spinnman.processes.abstract_process import AbstractProcess
from spinnman.messages.scp.impl.scp_version_request import SCPVersionRequest


class GetVersionProcess(AbstractProcess):

    def __init__(self, connection):
        AbstractProcess.__init__(self)
        self._scp_request_set = SCPRequestSet(connection)
        self._version_info = None

    def _get_response(self, version_response):
        self._version_info = version_response.version_info

    def get_version(self):
        self._scp_request_set.send_request(
            SCPVersionRequest(x=0, y=0, p=0),
            self._get_response, self._receive_error)
        self._scp_request_set.finish()

        self.check_for_error()
        return self._version_info
