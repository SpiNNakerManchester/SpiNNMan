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
from .udp_connection import UDPConnection
from spinnman.messages.spinnaker_boot import SpinnakerBootMessage
from spinnman.constants import UDP_BOOT_CONNECTION_DEFAULT_PORT

_ANTI_FLOOD_DELAY = 0.1


class BootConnection(UDPConnection):
    """ A connection to the SpiNNaker board that uses UDP to for booting
    """
    __slots__ = []
    _REPR_TEMPLATE = (
        "BootConnection(local_host={}, local_port={}, remote_host={}, "
        "remote_port={})")

    def __init__(self, remote_host=None):
        """
        :param str remote_host:
            The remote host name or IP address to send packets to.  If not
            specified, the socket will be available for listening only, and
            will throw and exception if used for sending
        :raise SpinnmanIOException:
            If there is an error setting up the communication channel
        """
        super().__init__(remote_host=remote_host,
                         remote_port=UDP_BOOT_CONNECTION_DEFAULT_PORT)

    def send_boot_message(self, boot_message):
        """ Sends a SpiNNaker boot message using this connection.

        :param SpinnakerBootMessage boot_message: The message to be sent
        :raise SpinnmanIOException:
            If there is an error sending the message
        """
        self.send(boot_message.bytestring)

        # Sleep between messages to avoid flooding the machine
        time.sleep(_ANTI_FLOOD_DELAY)

    def receive_boot_message(self, timeout=None):
        """ Receives a boot message from this connection.  Blocks until a\
            message has been received, or a timeout occurs.

        :param int timeout:
            The time in seconds to wait for the message to arrive; if not
            specified, will wait forever, or until the connection is closed.
        :return: a boot message
        :rtype: SpinnakerBootMessage
        :raise SpinnmanIOException:
            If there is an error receiving the message
        :raise SpinnmanTimeoutException:
            If there is a timeout before a message is received
        :raise SpinnmanInvalidPacketException:
            If the received packet is not a valid SpiNNaker boot message
        :raise SpinnmanInvalidParameterException:
            If one of the fields of the SpiNNaker boot message is invalid
        """
        data = self.receive(timeout)
        return SpinnakerBootMessage.from_bytestring(data, 0)

    def __repr__(self):
        return self._REPR_TEMPLATE.format(
            self.local_ip_address, self.local_port,
            self.remote_ip_address, self.remote_port)
