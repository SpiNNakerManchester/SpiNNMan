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

import struct
import time
from typing import Callable
from spinn_utilities.abstract_base import AbstractBase
from spinn_utilities.overrides import overrides
from spinnman.connections.abstract_classes import Listenable
from spinnman.connections.udp_packet_connections import BootConnection
from spinnman.connections.udp_packet_connections.boot_connection import (
    _ANTI_FLOOD_DELAY)
from spinnman.messages.spinnaker_boot import SpinnakerBootMessage
from .spalloc_proxied_connection import SpallocProxiedConnection

_ONE_SHORT = struct.Struct("<H")
_TWO_SHORTS = struct.Struct("<2H")
_TWO_SKIP: bytes = b'\0\0'
_NUM_UPDATE_TAG_TRIES = 3
_UPDATE_TAG_TIMEOUT = 1.0


class SpallocBootConnection(
        BootConnection, SpallocProxiedConnection, metaclass=AbstractBase):
    """
    The socket interface supported by proxied boot sockets. The socket will
    always be talking to the root board of a job.
    This emulates a BootConnection.
    """
    __slots__ = ()

    @overrides(BootConnection.send_boot_message)
    def send_boot_message(self, boot_message: SpinnakerBootMessage):
        self.send(boot_message.bytestring)

        # Sleep between messages to avoid flooding the machine
        time.sleep(_ANTI_FLOOD_DELAY)

    @overrides(BootConnection.receive_boot_message)
    def receive_boot_message(self, timeout=None) -> SpinnakerBootMessage:
        data = self.receive(timeout)
        return SpinnakerBootMessage.from_bytestring(data, 0)

    @overrides(Listenable.get_receive_method)
    def get_receive_method(self) -> Callable:
        return self.receive_boot_message
