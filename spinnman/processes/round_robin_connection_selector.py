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
from .abstract_multi_connection_process_connection_selector import (
    AbstractMultiConnectionProcessConnectionSelector)


class RoundRobinConnectionSelector(
        AbstractMultiConnectionProcessConnectionSelector):
    """
    A connection selector that just spreads work as evenly as possible.
    """
    __slots__ = [
        "_connections",
        "_next_connection_index"]

    def __init__(self, connections):
        """
        :param list(SCAMPConnection) connections:
            The connections to be used
        """
        self._connections = connections
        self._next_connection_index = 0

    @overrides(
        AbstractMultiConnectionProcessConnectionSelector.get_next_connection)
    def get_next_connection(self, message):
        index = self._next_connection_index
        self._next_connection_index = (index + 1) % len(self._connections)
        return self._connections[index]
