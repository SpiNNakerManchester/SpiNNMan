# Copyright (c) 2014 The University of Manchester
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
from typing import Optional, Tuple
from spinn_utilities.abstract_base import AbstractBase, abstractmethod
from spinnman.messages.scp.enums import SCPResult
from spinnman.messages.scp.abstract_messages import AbstractSCPRequest
from .connection import Connection


class AbstractSCPConnection(Connection, metaclass=AbstractBase):
    """
    A sender and receiver of SCP messages.
    """

    __slots__ = ()

    @abstractmethod
    def is_ready_to_receive(self, timeout: float = 0) -> bool:
        """
        Determines if there is an SCP packet to be read without blocking.

        :param timeout:
            The time to wait before returning if the connection is not ready
        :return: True if there is an SCP packet to be read
        """
        raise NotImplementedError

    @abstractmethod
    def receive_scp_response(self, timeout: Optional[float] = 1.0) -> Tuple[
            SCPResult, int, bytes, int]:
        """
        Receives an SCP response from this connection.  Blocks
        until a message has been received, or a timeout occurs.

        :param timeout:
            The time in seconds to wait for the message to arrive; if `None`,
            will wait forever, or until the connection is closed
        :return: The SCP result, the sequence number, the data of the response
            and the offset at which the data starts (i.e., where the SDP
            header starts).
        :raise SpinnmanIOException:
            If there is an error receiving the message
        :raise SpinnmanTimeoutException:
            If there is a timeout before a message is received
        """
        raise NotImplementedError

    @abstractmethod
    def get_scp_data(self, scp_request: AbstractSCPRequest) -> bytes:
        """
        :returns: the data of an SCP request as it would be sent down this
           connection.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def chip_x(self) -> int:
        """
        The X-coordinate of the chip at which messages sent down this
        connection will arrive at first.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def chip_y(self) -> int:
        """
        The Y-coordinate of the chip at which messages sent down this
        connection will arrive at first.
        """
        raise NotImplementedError
