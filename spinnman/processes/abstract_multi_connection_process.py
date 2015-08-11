from spinnman.processes.abstract_process import AbstractProcess
from spinnman.connections.scp_request_set import SCPRequestSet
from spinnman.processes.abstract_multi_connection_process_connection_selector \
    import AbstractMultiConnectionProcessConnectionSelector


class MultiConnectionProcessDefaultConnectionSelector(
        AbstractMultiConnectionProcessConnectionSelector):

    def __init__(self, connections):
        AbstractMultiConnectionProcessConnectionSelector.__init__(
            self, connections)
        self._connections = connections
        self._next_connection_index = 0

    def get_next_connection(self, message):
        index = self._next_connection_index
        self._next_connection_index = (index + 1) % len(self._connections)
        return index


class AbstractMultiConnectionProcess(AbstractProcess):
    """ A process that uses multiple connections in communication
    """

    def __init__(self, connections, next_connection_selector=None,
                 n_retries=3, timeout=0.5, n_channels=4,
                 intermediate_channel_waits=2):
        AbstractProcess.__init__(self)
        self._scp_request_sets = list()
        for connection in connections:
            scp_request_set = SCPRequestSet(
                connection, n_retries=n_retries, packet_timeout=timeout,
                n_channels=n_channels,
                intermediate_channel_waits=intermediate_channel_waits)
            self._scp_request_sets.append(scp_request_set)
        self._next_connection_selector = next_connection_selector
        if next_connection_selector is None:
            self._next_connection_selector = \
                MultiConnectionProcessDefaultConnectionSelector(connections)
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
