from spinnman.processes.abstract_multi_connection_process_connection_selector \
    import AbstractMultiConnectionProcessConnectionSelector


class MultiConnectionProcessMostDirectConnectionSelector(
        AbstractMultiConnectionProcessConnectionSelector):

    def __init__(self, machine, connections):
        AbstractMultiConnectionProcessConnectionSelector.__init__(
            self, connections)
        self._machine = machine
        self._connections = dict()
        index = 0
        for connection in connections:
            self._connections[
                (connection.chip_x, connection.chip_y)] = index
            index += 1

    def get_next_connection(self, message):
        chip = self._machine.get_chip_at(message.sdp_header.destination_chip_x,
                                         message.sdp_header.destination_chip_y)
        index = self._connections[(chip.nearest_ethernet_x,
                                   chip.nearest_ethernet_y)]
        return index
