# Copyright (c) 2022 The University of Manchester
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
"""
API of the client for the Spalloc web service.
"""

from spinn_utilities.abstract_base import AbstractBase, abstractmethod
from spinnman.connections.abstract_classes import Listenable


class SpallocProxiedConnection(Listenable, metaclass=AbstractBase):
    """
    Base class for connections proxied via Spalloc.
    """
    __slots__ = ()

    @abstractmethod
    def send(self, data: bytes):
        """
        Send a message on an open socket.

        :param data: The message to send.
        """

    @abstractmethod
    def receive(self, timeout=None) -> bytes:
        """
        Receive a message on an open socket. Will block until a message is
        received.

        :param timeout:
            How long to wait for a message to be received before timing out.
            If None, will wait indefinitely (or until the connection is
            closed).
        :return: The received message.
        :raises SpinnmanTimeoutException:
            If a timeout happens
        """
