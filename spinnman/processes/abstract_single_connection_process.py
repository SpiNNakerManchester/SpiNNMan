from spinnman.processes.abstract_process import AbstractProcess
from spinnman.connections.scp_request_set import SCPRequestSet


class AbstractSingleConnectionProcess(AbstractProcess):
    """ A process that uses a single connection in communication
    """

    def __init__(self, connection):
        AbstractProcess.__init__(self)
        self._scp_request_set = SCPRequestSet(connection)

    def _send_request(self, request, callback=None, error_callback=None):
        if error_callback is None:
            error_callback = self._receive_error
        self._scp_request_set.send_request(request, callback, error_callback)

    def _finish(self):
        self._scp_request_set.finish()
