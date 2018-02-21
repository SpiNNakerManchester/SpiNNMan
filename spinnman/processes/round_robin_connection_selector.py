from .abstract_multi_connection_process_connection_selector \
    import AbstractMultiConnectionProcessConnectionSelector


class RoundRobinConnectionSelector(
        AbstractMultiConnectionProcessConnectionSelector):
    __slots__ = [
        "_connections",
        "_next_connection_index"]

    def __init__(self, connections):
        super(RoundRobinConnectionSelector, self).__init__(connections)
        self._connections = connections
        self._next_connection_index = 0

    def get_next_connection(self, message):
        index = self._next_connection_index
        self._next_connection_index = (index + 1) % len(self._connections)
        return self._connections[index]
