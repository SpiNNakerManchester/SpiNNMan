# Copyright (c) 2014 The University of Manchester
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

import time
from .udp_connection import UDPConnection
from spinnman.messages.spinnaker_boot import SpinnakerBootMessage
from spinnman.constants import UDP_BOOT_CONNECTION_DEFAULT_PORT

_ANTI_FLOOD_DELAY = 0.1


class BootConnection(UDPConnection):
    """
    A connection to the SpiNNaker board that uses UDP to for booting.
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
        """
        Sends a SpiNNaker boot message using this connection.

        :param SpinnakerBootMessage boot_message: The message to be sent
        :raise SpinnmanIOException:
            If there is an error sending the message
        """
        self.send(boot_message.bytestring)

        # Sleep between messages to avoid flooding the machine
        time.sleep(_ANTI_FLOOD_DELAY)

    def receive_boot_message(self, timeout=None):
        """
        Receives a boot message from this connection.  Blocks until a
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
