# Copyright (c) 2015 The University of Manchester
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from spinn_utilities.overrides import overrides
from spinnman.data import SpiNNManDataView
from .abstract_multi_connection_process_connection_selector import (
    AbstractMultiConnectionProcessConnectionSelector)


class MostDirectConnectionSelector(
        AbstractMultiConnectionProcessConnectionSelector):
    """
    A selector that goes for the most direct connection for the message.
    """
    __slots__ = (
        "_connections",
        "_lead_connection")

    def __init__(self, connections):
        """
        :param list(SCAMPConnection) connections:
            The connections to be used
        """
        self._connections = dict()
        self._lead_connection = None
        for conn in connections:
            if conn.chip_x == 0 and conn.chip_y == 0:
                self._lead_connection = conn
            self._connections[conn.chip_x, conn.chip_y] = conn
        if self._lead_connection is None:
            self._lead_connection = next(iter(connections))

    @overrides(
        AbstractMultiConnectionProcessConnectionSelector.get_next_connection)
    def get_next_connection(self, message):
        key = (message.sdp_header.destination_chip_x,
               message.sdp_header.destination_chip_y)
        if key in self._connections:
            return self._connections[key]

        if not SpiNNManDataView.has_machine() or len(self._connections) == 1:
            return self._lead_connection

        x, y = key
        key = SpiNNManDataView.get_nearest_ethernet(x, y)

        return self._connections.get(key, self._lead_connection)
