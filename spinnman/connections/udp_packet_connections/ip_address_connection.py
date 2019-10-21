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

from .udp_connection import UDPConnection
from spinnman.constants import UDP_BOOT_CONNECTION_DEFAULT_PORT

_BOOTROM_SPINN_PORT = 54321  # Matches SPINN_PORT in spinnaker_bootROM


class IPAddressesConnection(UDPConnection):
    """ A connection that detects any UDP packet that is transmitted by\
        SpiNNaker boards prior to boot
    """
    __slots__ = []

    def __init__(self, local_host=None,
                 local_port=UDP_BOOT_CONNECTION_DEFAULT_PORT):
        super(IPAddressesConnection, self).__init__(
            local_host=local_host, local_port=local_port)

    def supports_sends_message(self, message):  # @UnusedVariable
        # pylint: disable=unused-argument
        return False

    def receive_ip_address(self, timeout=None):
        try:
            (_, (ip_address, port)) = self.receive_with_address(timeout)
            if port == _BOOTROM_SPINN_PORT:
                return ip_address
        except Exception:  # pylint: disable=broad-except
            pass
        return None

    def __repr__(self):
        return "IPAddressesConnection(local_host={}, local_port={})".format(
            self.local_ip_address, self.local_port)
