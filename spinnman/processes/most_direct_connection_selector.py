from .abstract_multi_connection_process_connection_selector \
    import AbstractMultiConnectionProcessConnectionSelector


class MostDirectConnectionSelector(
        AbstractMultiConnectionProcessConnectionSelector):
    """
    MostDirectConnectionSelector: selector that goes for the most direct \
    connection for the message
    """

    def __init__(self, machine, connections):
        AbstractMultiConnectionProcessConnectionSelector.__init__(
            self, connections)
        self._machine = machine
        self._connections = dict()
        self._first_connection = None
        for connection in connections:
            if connection.chip_x == 0 and connection.chip_y == 0:
                self._first_connection = connection
            self._connections[
                (connection.chip_x, connection.chip_y)] = connection
        if self._first_connection is None:
            self._first_connection = next(iter(connections))

    def set_machine(self, new_machine):
        self._machine = new_machine

    def get_next_connection(self, message):
        if self._machine is None or len(self._connections) == 1:
            return self._first_connection

        chip = self._machine.get_chip_at(
            message.sdp_header.destination_chip_x,
            message.sdp_header.destination_chip_y)
        key = (chip.nearest_ethernet_x, chip.nearest_ethernet_y)

        if key not in self._connections:
            return self._first_connection
        return self._connections[key]
