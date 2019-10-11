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


class RoundRobinConnectionSelector(
        AbstractMultiConnectionProcessConnectionSelector):
    __slots__ = [
        "_connections",
        "_next_connection_index"]

    @overrides(AbstractMultiConnectionProcessConnectionSelector.__init__)
    def __init__(self, connections):  # pylint: disable=super-init-not-called
        self._connections = connections
        self._next_connection_index = 0

    @overrides(
        AbstractMultiConnectionProcessConnectionSelector.get_next_connection)
    def get_next_connection(self, message):
        index = self._next_connection_index
        self._next_connection_index = (index + 1) % len(self._connections)
        return self._connections[index]
