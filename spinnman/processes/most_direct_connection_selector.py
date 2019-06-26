from spinn_utilities.overrides import overrides
from .abstract_multi_connection_process_connection_selector import (
    AbstractMultiConnectionProcessConnectionSelector)
from spinn_machine.spinnaker_triad_geometry import SpiNNakerTriadGeometry


class MostDirectConnectionSelector(
        AbstractMultiConnectionProcessConnectionSelector):
    """ A selector that goes for the most direct connection for the message.
    """
    __slots__ = [
        "_connections",
        "_first_connection",
        "_width",
        "_height"]

    geometry = SpiNNakerTriadGeometry.get_spinn5_geometry()

    @overrides(AbstractMultiConnectionProcessConnectionSelector.__init__)
    def __init__(self, width, height, connections):
        self._width = width
        self._height = height
        self._connections = dict()
        self._first_connection = None
        for connection in connections:
            if connection.chip_x == 0 and connection.chip_y == 0:
                self._first_connection = connection
            self._connections[
                (connection.chip_x, connection.chip_y)] = connection
        if self._first_connection is None:
            self._first_connection = next(iter(connections))

    def set_dims(self, width, height):
        self._width = width
        self._height = height

    @overrides(
        AbstractMultiConnectionProcessConnectionSelector.get_next_connection)
    def get_next_connection(self, message):
        if (self._width is None or self._height is None or
                len(self._connections) == 1):
            return self._first_connection

        key = self.geometry.get_ethernet_chip_coordinates(
            message.sdp_header.destination_chip_x,
            message.sdp_header.destination_chip_y,
            self._width, self._height)

        if key not in self._connections:
            return self._first_connection
        return self._connections[key]
