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
from contextlib import suppress
from spinnman.constants import UDP_BOOT_CONNECTION_DEFAULT_PORT
from .udp_connection import UDPConnection

_BOOTROM_SPINN_PORT = 54321  # Matches SPINN_PORT in spinnaker_bootROM


class IPAddressesConnection(UDPConnection):
    """
    A connection that detects any UDP packet that is transmitted by
    SpiNNaker boards prior to boot.
    """
    __slots__ = []

    def __init__(self, local_host=None,
                 local_port=UDP_BOOT_CONNECTION_DEFAULT_PORT):
        super().__init__(local_host=local_host, local_port=local_port)

    def receive_ip_address(self, timeout=None):
        with suppress(Exception):
            (_, (ip_address, port)) = self.receive_with_address(timeout)
            if port == _BOOTROM_SPINN_PORT:
                return ip_address
        return None

    def __repr__(self):
        return "IPAddressesConnection(local_host={}, local_port={})".format(
            self.local_ip_address, self.local_port)
