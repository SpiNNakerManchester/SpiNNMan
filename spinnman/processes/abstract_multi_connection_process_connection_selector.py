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

from typing import Generic, TypeVar
from spinn_utilities.abstract_base import (
    AbstractBase, abstractmethod)
from spinnman.messages.scp.abstract_messages import AbstractSCPRequest
from spinnman.connections.udp_packet_connections import (
    BMPConnection, SCAMPConnection)

#: Type of connections selected between.
#: :meta private:
Conn = TypeVar("Conn", SCAMPConnection, BMPConnection)


class ConnectionSelector(Generic[Conn], metaclass=AbstractBase):
    """
    A connection selector for multi-connection processes.
    """
    __slots__ = ()

    @abstractmethod
    def get_next_connection(
            self, message: AbstractSCPRequest) -> Conn:
        """
        :param message: The SCP message to be sent
        :returns: The (next) available Connection
        """
        raise NotImplementedError
