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

from spinn_utilities.abstract_base import AbstractBase, abstractmethod
from .connection import Connection


class SDPReceiver(Connection, metaclass=AbstractBase):
    """ A receiver of SDP messages
    """

    __slots__ = ()

    @abstractmethod
    def receive_sdp_message(self, timeout=None):
        """ Receives an SDP message from this connection.  Blocks until the\
            message has been received, or a timeout occurs.

        :param int timeout:
            The time in seconds to wait for the message to arrive; if not
            specified, will wait forever, or until the connection is closed.
        :return: The received SDP message
        :rtype: SDPMessage
        :raise SpinnmanIOException:
            If there is an error receiving the message
        :raise SpinnmanTimeoutException:
            If there is a timeout before a message is received
        :raise SpinnmanInvalidPacketException:
            If the received packet is not a valid SDP message
        :raise SpinnmanInvalidParameterException:
            If one of the fields of the SDP message is invalid
        """
