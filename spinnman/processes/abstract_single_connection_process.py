from .abstract_process import AbstractProcess
from spinnman.connections import SCPRequestPipeLine


class AbstractSingleConnectionProcess(AbstractProcess):
    """ A process that uses a single connection in communication.
    """
    __slots__ = [
        "_connection_selector",
        "_scp_request_pipeline"]

    def __init__(self, connection_selector):
        super(AbstractSingleConnectionProcess, self).__init__()
        self._scp_request_pipeline = None
        self._connection_selector = connection_selector

    def _send_request(self, request, callback=None, error_callback=None):
        if error_callback is None:
            error_callback = self._receive_error

        # If no pipe line built yet, build one on the connection selected for
        # it
        if self._scp_request_pipeline is None:
            self._scp_request_pipeline = SCPRequestPipeLine(
                self._connection_selector.get_next_connection(request))

        # send request
        self._scp_request_pipeline.send_request(
            request, callback, error_callback)

    def _finish(self):
        self._scp_request_pipeline.finish()
