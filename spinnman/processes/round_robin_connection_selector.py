from .abstract_multi_connection_process_connection_selector \
    import AbstractMultiConnectionProcessConnectionSelector


class RoundRobinConnectionSelector(
        AbstractMultiConnectionProcessConnectionSelector):
    """
    RoundRobinConnectionSelector: selector
    """

    def __init__(self, connections):
        AbstractMultiConnectionProcessConnectionSelector.__init__(
            self, connections)
        self._connections = connections
        self._next_connection_index = 0

    def get_next_connection(self, message):
        index = self._next_connection_index
        self._next_connection_index = (index + 1) % len(self._connections)
        return self._connections[index]
