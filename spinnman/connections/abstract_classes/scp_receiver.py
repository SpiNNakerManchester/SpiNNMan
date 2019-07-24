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

from six import add_metaclass
from spinn_utilities.abstract_base import AbstractBase, abstractmethod
from .connection import Connection


@add_metaclass(AbstractBase)
class SCPReceiver(Connection):
    """ A receiver of SCP messages
    """

    __slots__ = ()

    @abstractmethod
    def is_ready_to_receive(self, timeout=0):
        """ Determines if there is an SCP packet to be read without blocking

        :param timeout: \
            The time to wait before returning if the connection is not ready
        :type timeout: int
        :return: True if there is an SCP packet to be read
        :rtype: bool
        """

    @abstractmethod
    def receive_scp_response(self, timeout=1.0):
        """ Receives an SCP response from this connection.  Blocks\
            until a message has been received, or a timeout occurs.

        :param timeout: \
            The time in seconds to wait for the message to arrive; if not\
            specified, will wait forever, or until the connection is closed
        :type timeout: int
        :return: The SCP result, the sequence number, the data of the response\
            and the offset at which the data starts (i.e., where the SDP\
            header starts).
        :rtype: tuple(:py:class:`spinnman.messages.scp.scp_result.SCPResult`,\
            int, bytestring, int)
        :raise spinnman.exceptions.SpinnmanIOException: \
            If there is an error receiving the message
        :raise spinnman.exceptions.SpinnmanTimeoutException: \
            If there is a timeout before a message is received
        """
