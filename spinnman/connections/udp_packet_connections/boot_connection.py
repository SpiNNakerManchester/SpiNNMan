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

import time
from spinn_utilities.overrides import overrides
from spinnman.connections.abstract_classes import (
    SpinnakerBootSender, SpinnakerBootReceiver)
from .udp_connection import UDPConnection
from spinnman.messages.spinnaker_boot import SpinnakerBootMessage
from spinnman.constants import UDP_BOOT_CONNECTION_DEFAULT_PORT

_ANTI_FLOOD_DELAY = 0.1


class BootConnection(
        UDPConnection, SpinnakerBootSender, SpinnakerBootReceiver):
    """ A connection to the SpiNNaker board that uses UDP to for booting
    """
    __slots__ = []

    def __init__(self, local_host=None, local_port=None, remote_host=None,
                 remote_port=None):
        """
        :param local_host: The local host name or IP address to bind to.\
            If not specified defaults to bind to all interfaces, unless\
            remote_host is specified, in which case binding is done to the\
            IP address that will be used to send packets.
        :type local_host: str
        :param local_port: The local port to bind to, between 1025 and 65535.\
            If not specified, defaults to a random unused local port
        :type local_port: int
        :param remote_host: The remote host name or IP address to send packets\
            to.  If not specified, the socket will be available for listening\
            only, and will throw and exception if used for sending
        :type remote_host: str
        :param remote_port: The remote port to send packets to.  If\
            remote_host is None, this is ignored.
        :type remote_port: int
        :raise spinnman.exceptions.SpinnmanIOException: \
            If there is an error setting up the communication channel
        """

        if remote_port is None:
            remote_port = UDP_BOOT_CONNECTION_DEFAULT_PORT

        super(BootConnection, self).__init__(
            local_host, local_port, remote_host, remote_port)

    @overrides(SpinnakerBootSender.send_boot_message)
    def send_boot_message(self, boot_message):
        self.send(boot_message.bytestring)

        # Sleep between messages to avoid flooding the machine
        time.sleep(_ANTI_FLOOD_DELAY)

    @overrides(SpinnakerBootReceiver.receive_boot_message)
    def receive_boot_message(self, timeout=None):
        data = self.receive(timeout)
        return SpinnakerBootMessage.from_bytestring(data, 0)

    def __repr__(self):
        return\
            "BootConnection(local_host={}, local_port={}, remote_host={},"\
            "remote_port={})".format(
                self.local_ip_address, self.local_port,
                self.remote_ip_address, self.remote_port)
