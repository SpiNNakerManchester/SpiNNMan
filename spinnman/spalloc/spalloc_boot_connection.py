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
