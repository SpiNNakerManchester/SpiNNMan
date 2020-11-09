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


class MostDirectConnectionSelector(
        AbstractMultiConnectionProcessConnectionSelector):
    """ A selector that goes for the most direct connection for the message.
    """
    __slots__ = [
        "_connections",
        "_first_connection",
        "_machine"]

    # pylint: disable=super-init-not-called
    def __init__(self, machine, connections):
        """
        :param ~spinn_machine.Machine machine:
        :param list(SCAMPConnection) connections:
            The connections to be used
        """
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
        """
        :param ~spinn_machine.Machine new_machine:
        """
        self._machine = new_machine

    @overrides(
        AbstractMultiConnectionProcessConnectionSelector.get_next_connection)
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
