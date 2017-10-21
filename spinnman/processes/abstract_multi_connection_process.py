from .abstract_process import AbstractProcess
from spinnman.connections import SCPRequestPipeLine


class AbstractMultiConnectionProcess(AbstractProcess):
    """ A process that uses multiple connections in communication
    """

    def __init__(self, next_connection_selector,
                 n_retries=3, timeout=0.5, n_channels=1,
                 intermediate_channel_waits=0):
        AbstractProcess.__init__(self)
        self._scp_request_pipe_lines = dict()
        self._n_retries = n_retries
        self._timeout = timeout
        self._n_channels = n_channels
        self._intermediate_channel_waits = intermediate_channel_waits
        self._next_connection_selector = next_connection_selector

    def _send_request(self, request, callback=None, error_callback=None):
        if error_callback is None:
            error_callback = self._receive_error
        connection = self._next_connection_selector.get_next_connection(
            request)
        if connection not in self._scp_request_pipe_lines:
            scp_request_set = SCPRequestPipeLine(
                connection, n_retries=self._n_retries,
                packet_timeout=self._timeout,
                n_channels=self._n_channels,
                intermediate_channel_waits=self._intermediate_channel_waits)
            self._scp_request_pipe_lines[connection] = scp_request_set
        self._scp_request_pipe_lines[connection].send_request(
            request, callback, error_callback)

    def _finish(self):
        for request_pipeline in self._scp_request_pipe_lines.itervalues():
            request_pipeline.finish()
