# Copyright (c) 2017-2019 The University of Manchester
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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

    # pylint: disable=super-init-not-called
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
