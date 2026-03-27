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
from typing import Any, List
from spinn_utilities.overrides import overrides
from spinnman.connections.udp_packet_connections import SCAMPConnection
from .abstract_multi_connection_process_connection_selector import (
    ConnectionSelector)


class RoundRobinConnectionSelector(ConnectionSelector):
    """
    A connection selector that just spreads work as evenly as possible.
    """
    __slots__ = (
        "_connections",
        "_next_connection_index")

    def __init__(self, connections: List[SCAMPConnection]):
        """
        :param connections: The connections to be used
        """
        self._connections = connections
        self._next_connection_index = 0

    @overrides(ConnectionSelector.get_next_connection)
    def get_next_connection(self, message: Any) -> SCAMPConnection:
        index = self._next_connection_index
        self._next_connection_index = (index + 1) % len(self._connections)
        return self._connections[index]
