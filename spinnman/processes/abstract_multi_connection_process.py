from spinnman.processes.abstract_process import AbstractProcess
from spinnman.connections.scp_request_set import SCPRequestSet


class AbstractMultiConnectionProcess(AbstractProcess):
    """ A process that uses multiple connections in communication
    """

    def __init__(self, connections, next_connection_selector,
                 n_retries=3, timeout=0.5, n_channels=1,
                 intermediate_channel_waits=0):
        AbstractProcess.__init__(self)
        self._scp_request_sets = list()
        for connection in connections:
            scp_request_set = SCPRequestSet(
                connection, n_retries=n_retries, packet_timeout=timeout,
                n_channels=n_channels,
                intermediate_channel_waits=intermediate_channel_waits)
            self._scp_request_sets.append(scp_request_set)
        self._next_connection_selector = next_connection_selector
        self._connections_used = set()

    def _send_request(self, request, callback=None, error_callback=None):
        if error_callback is None:
            error_callback = self._receive_error
        index = self._next_connection_selector.get_next_connection(request)
        self._scp_request_sets[index].send_request(
            request, callback, error_callback)
        self._connections_used.add(index)

    def _finish(self):
        for index in self._connections_used:
            self._scp_request_sets[index].finish()
        self._connections_used = set()
