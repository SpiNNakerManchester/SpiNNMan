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

from spinn_utilities.abstract_base import (
    AbstractBase, abstractmethod, abstractproperty)
from .connection import Connection


class AbstractSCPConnection(Connection, metaclass=AbstractBase):
    """
    A sender and receiver of SCP messages.
    """

    __slots__ = ()

    @abstractmethod
    def is_ready_to_receive(self, timeout=0):
        """
        Determines if there is an SCP packet to be read without blocking.

        :param int timeout:
            The time to wait before returning if the connection is not ready
        :return: True if there is an SCP packet to be read
        :rtype: bool
        """

    @abstractmethod
    def receive_scp_response(self, timeout=1.0):
        """
        Receives an SCP response from this connection.  Blocks
        until a message has been received, or a timeout occurs.

        :param int timeout:
            The time in seconds to wait for the message to arrive; if not
            specified, will wait forever, or until the connection is closed
        :return: The SCP result, the sequence number, the data of the response
            and the offset at which the data starts (i.e., where the SDP
            header starts).
        :rtype: tuple(SCPResult, int, bytes, int)
        :raise SpinnmanIOException:
            If there is an error receiving the message
        :raise SpinnmanTimeoutException:
            If there is a timeout before a message is received
        """

    @abstractmethod
    def get_scp_data(self, scp_request):
        """
        Returns the data of an SCP request as it would be sent down this
        connection.
        """

    @abstractmethod
    def send_scp_request(self, scp_request):
        """
        Sends an SCP request down this connection.

        Messages must have the following properties:

            * source_port is `None` or 7
            * source_cpu is `None` or 31
            * source_chip_x is `None` or 0
            * source_chip_y is `None` or 0

        tag in the message is optional; if not set, the default set in the
        constructor will be used.
        sequence in the message is optional; if not set, (sequence number
        last assigned + 1) % 65536 will be used

        :param AbstractSCPRequest scp_request: message packet to send
        :raise SpinnmanIOException:
            If there is an error sending the message
        """

    @abstractproperty
    def chip_x(self):
        """
        The X-coordinate of the chip at which messages sent down this
        connection will arrive at first.

        :rtype: int
        """

    @abstractproperty
    def chip_y(self):
        """
        The Y-coordinate of the chip at which messages sent down this
        connection will arrive at first.

        :rtype: int
        """
