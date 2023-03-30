# Copyright (c) 2022 The University of Manchester
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
            If `None`, will wait indefinitely (or until the connection is
            closed).
        :return: The received message.
        :raises SpinnmanTimeoutException:
            If a timeout happens
        """
