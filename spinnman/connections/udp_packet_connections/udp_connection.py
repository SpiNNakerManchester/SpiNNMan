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

import logging
import socket
import select
from contextlib import suppress
from spinn_utilities.log import FormatAdapter
from spinn_utilities.overrides import overrides
from spinn_utilities.ping import Ping
from spinnman.exceptions import (SpinnmanIOException, SpinnmanEOFException)
from spinnman.connections.abstract_classes import Connection
from spinnman.utilities.socket_utils import (
    bind_socket, connect_socket, get_udp_socket, get_socket_address,
    resolve_host, set_receive_buffer_size, receive_message,
    receive_message_and_address, send_message, send_message_to_address)
from spinnman.connections.abstract_classes import Listenable

logger = FormatAdapter(logging.getLogger(__name__))
_RECEIVE_BUFFER_SIZE = 1048576
_PING_COUNT = 5
_REPR_TEMPLATE = "UDPConnection(local={}:{}, remote={}:{})"


class UDPConnection(Connection, Listenable):
    """
    A connection that routes messages via UDP to some remote host.

    Subclasses of this should be aware that UDP messages may be dropped,
    reordered, or duplicated, and that there's no way to tell whether the
    other end of the connection truly exists except by listening for
    occasional messages from them. There is also an upper size limit on
    messages, formally of 64kB, but usually of about 1500 bytes (the typical
    maximum size of an Ethernet packet);
    SDP messages have lower maximum lengths.
    """

    __slots__ = [
        "_can_send",
        "_local_ip_address",
        "_local_port",
        "_remote_ip_address",
        "_remote_port",
        "_socket"]

    def __init__(self, local_host=None, local_port=None, remote_host=None,
                 remote_port=None):
        """
        :param str local_host: The local host name or IP address to bind to.
            If not specified defaults to bind to all interfaces, unless
            remote_host is specified, in which case binding is done to the
            IP address that will be used to send packets
        :param int local_port: The local port to bind to, between 1025 and
            65535. If not specified, defaults to a random unused local port
        :param str remote_host: The remote host name or IP address to send
            packets to. If not specified, the socket will be available for
            listening only, and will throw and exception if used for sending
        :param int remote_port: The remote port to send packets to.  If
            remote_host is None, this is ignored.  If remote_host is specified
            specified, this must also be specified for the connection to allow
            sending
        :raise SpinnmanIOException:
            If there is an error setting up the communication channel
        """

        self._socket = get_udp_socket()
        set_receive_buffer_size(self._socket, _RECEIVE_BUFFER_SIZE)

        # Get the host and port to bind to locally
        local_bind_host = "" if local_host is None else local_host
        local_bind_port = 0 if local_port is None else local_port
        bind_socket(self._socket, local_bind_host, local_bind_port)

        # Mark the socket as non-sending, unless the remote host is
        # specified - send requests will then cause an exception
        self._can_send = False
        self._remote_ip_address = None
        self._remote_port = None

        # Get the host to connect to remotely
        if remote_host is not None and remote_port is not None:
            self._remote_port = remote_port
            self._remote_ip_address = resolve_host(remote_host)
            connect_socket(self._socket, self._remote_ip_address, remote_port)
            self._can_send = True

        # If things are closed here, it's a catastrophic problem
        if self._socket._closed:
            raise SpinnmanEOFException()

        # Get the details of where the socket is connected
        self._local_ip_address, self._local_port = \
            get_socket_address(self._socket)

        # Set a general timeout on the socket
        self._socket.settimeout(1.0)

    @property
    def __is_closed(self):
        """
        Is the socket closed?

        .. note::
            Just because a socket is not closed doesn't mean that you're going
            to be able to successfully write to it or read from it; some
            failures are only detected on use. But closed sockets definitely
            behave in certain ways!

        :rtype: bool
        """
        # Reach into Python'#s guts
        return self._socket._closed  # pylint: disable=protected-access

    @overrides(Connection.is_connected)
    def is_connected(self):
        # Closed sockets are never connected!
        if self.__is_closed:
            return False

        # If this is not a sending socket, it is not connected
        if not self._can_send:
            return False

        # check if machine is active and on the network
        for _ in range(_PING_COUNT):
            # Assume connected if ping works
            if Ping.ping(self._remote_ip_address) == 0:
                return True

        # If the ping fails this number of times, the host cannot be contacted
        return False

    @property
    def local_ip_address(self):
        """
        The local IP address to which the connection is bound,
        as a dotted string, e.g., `0.0.0.0`.

        :rtype: str
        """
        return self._local_ip_address

    @property
    def local_port(self):
        """
        The number of the local port to which the connection is bound.

        :rtype: int
        """
        return self._local_port

    @property
    def remote_ip_address(self):
        """
        The remote IP address to which the connection is connected,
        or `None` if not connected remotely.

        :rtype: str
        """
        return self._remote_ip_address

    @property
    def remote_port(self):
        """
        The remote port number to which the connection is connected,
        or `None` if not connected remotely.

        :rtype: int
        """
        return self._remote_port

    def receive(self, timeout=None):
        """
        Receive data from the connection.

        :param float timeout: The timeout in seconds, or `None` to wait forever
        :return: The data received as a byte-string
        :rtype: bytes
        :raise SpinnmanTimeoutException:
            If a timeout occurs before any data is received
        :raise SpinnmanIOException: If an error occurs receiving the data
        """
        if self.__is_closed:
            raise SpinnmanEOFException()
        return receive_message(self._socket, timeout, 300)

    def receive_with_address(self, timeout=None):
        """
        Receive data from the connection along with the address where the
        data was received from.

        :param float timeout: The timeout, or `None` to wait forever
        :return: A tuple of the data received and a tuple of the
            (address, port) received from
        :rtype: tuple(bytes, tuple(str, int))
        :raise SpinnmanTimeoutException:
            If a timeout occurs before any data is received
        :raise SpinnmanIOException: If an error occurs receiving the data
        """
        if self.__is_closed:
            raise SpinnmanEOFException()
        return receive_message_and_address(self._socket, timeout, 300)

    def send(self, data):
        """
        Send data down this connection.

        :param data: The data to be sent
        :type data: bytes or bytearray
        :raise SpinnmanIOException: If there is an error sending the data
        """
        if self.__is_closed:
            raise SpinnmanEOFException()
        if not self._can_send:
            raise SpinnmanIOException(
                "Remote host and/or port not set - data cannot be sent with"
                " this connection")
        while not send_message(self._socket, data):
            if self.__is_closed:
                raise SpinnmanEOFException()

    def send_to(self, data, address):
        """
        Send data down this connection.

        :param data: The data to be sent as a byte-string
        :type data: bytes or bytearray
        :param tuple(str,int) address:
            A tuple of (address, port) to send the data to
        :raise SpinnmanIOException: If there is an error sending the data
        """
        if self.__is_closed:
            raise SpinnmanEOFException()
        while not send_message_to_address(self._socket, data, address):
            if self.__is_closed:
                raise SpinnmanEOFException()

    @overrides(Connection.close)
    def close(self):
        if self.__is_closed:
            return
        with suppress(Exception):
            self._socket.shutdown(socket.SHUT_WR)
        self._socket.close()

    def is_ready_to_receive(self, timeout=0):
        if self.__is_closed:
            return True
        return len(select.select([self._socket], [], [], timeout)[0]) == 1

    def __repr__(self):
        return _REPR_TEMPLATE.format(
            self.local_ip_address, self.local_port,
            self.remote_ip_address, self.remote_port)

    @overrides(Listenable.get_receive_method)
    def get_receive_method(self):
        return self.receive
