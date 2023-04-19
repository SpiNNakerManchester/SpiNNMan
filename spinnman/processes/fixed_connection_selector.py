# Copyright (c) 2017 The University of Manchester
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


class FixedConnectionSelector(
        AbstractMultiConnectionProcessConnectionSelector):
    """
    A connection selector that only uses a single connection.
    """
    __slots__ = ("__connection", )

    def __init__(self, connection):
        """
        :param SCAMPConnection connection:
            The connection to be used
        """
        self.__connection = connection

    @overrides(
        AbstractMultiConnectionProcessConnectionSelector.get_next_connection)
    def get_next_connection(self, message):
        return self.__connection
