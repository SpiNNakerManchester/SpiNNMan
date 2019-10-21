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

import logging
import socket
import select
from six import raise_from
from spinn_utilities.overrides import overrides
from spinnman.exceptions import SpinnmanIOException, SpinnmanTimeoutException
from spinnman.connections.abstract_classes import Connection
from .utils import (
    bind_socket, connect_socket, get_socket, get_socket_address, ping,
    resolve_host, set_receive_buffer_size)

logger = logging.getLogger(__name__)
_RECEIVE_BUFFER_SIZE = 1048576
_PING_COUNT = 5
_REPR_TEMPLATE = "UDPConnection(local={}:{}, remote={}:{})"


class UDPConnection(Connection):
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
        :param local_host: The local host name or IP address to bind to.\
            If not specified defaults to bind to all interfaces, unless\
            remote_host is specified, in which case binding is done to the\
            IP address that will be used to send packets
        :type local_host: str or None
        :param local_port: The local port to bind to, between 1025 and 65535.\
            If not specified, defaults to a random unused local port
        :type local_port: int
        :param remote_host: The remote host name or IP address to send packets\
            to. If not specified, the socket will be available for listening\
            only, and will throw and exception if used for sending
        :type remote_host: str or None
        :param remote_port: The remote port to send packets to.  If\
            remote_host is None, this is ignored.  If remote_host is specified\
            specified, this must also be specified for the connection to allow\
            sending
        :raise spinnman.exceptions.SpinnmanIOException: \
            If there is an error setting up the communication channel
        """

        self._socket = get_socket()
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

        # Get the details of where the socket is connected
        self._local_ip_address, self._local_port = \
            get_socket_address(self._socket)

        # Set a general timeout on the socket
        self._socket.settimeout(1.0)

    @overrides(Connection.is_connected)
    def is_connected(self):
        # If this is not a sending socket, it is not connected
        if not self._can_send:
            return False

        # check if machine is active and on the network
        for _ in range(_PING_COUNT):
            # Assume connected if ping works
            if ping(self._remote_ip_address).returncode == 0:
                return True

        # If the ping fails this number of times, the host cannot be contacted
        return False

    @property
    def local_ip_address(self):
        """ The local IP address to which the connection is bound.

        :return: The local IP address as a dotted string, e.g., 0.0.0.0
        :rtype: str
        :raise None: No known exceptions are thrown
        """
        return self._local_ip_address

    @property
    def local_port(self):
        """ The local port to which the connection is bound.

        :return: The local port number
        :rtype: int
        :raise None: No known exceptions are thrown
        """
        return self._local_port

    @property
    def remote_ip_address(self):
        """ The remote IP address to which the connection is connected.

        :return: The remote IP address as a dotted string, or None if not\
            connected remotely
        :rtype: str
        """
        return self._remote_ip_address

    @property
    def remote_port(self):
        """ The remote port to which the connection is connected.

        :return: The remote port, or None if not connected remotely
        :rtype: int
        """
        return self._remote_port

    def receive(self, timeout=None):
        """ Receive data from the connection

        :param timeout: The timeout in seconds, or None to wait forever
        :type timeout: None or float
        :return: The data received as a bytestring
        :rtype: str
        :raise SpinnmanTimeoutException: \
            If a timeout occurs before any data is received
        :raise SpinnmanIOException: If an error occurs receiving the data
        """
        try:
            self._socket.settimeout(timeout)
            return self._socket.recv(300)
        except socket.timeout as e:
            raise_from(SpinnmanTimeoutException("receive", timeout), e)
        except Exception as e:  # pylint: disable=broad-except
            raise_from(SpinnmanIOException(str(e)), e)

    def receive_with_address(self, timeout=None):
        """ Receive data from the connection along with the address where the\
            data was received from

        :param timeout: The timeout, or None to wait forever
        :type timeout: None
        :return: A tuple of the data received and a tuple of the\
            (address, port) received from
        :rtype: str, (str, int)
        :raise SpinnmanTimeoutException: \
            If a timeout occurs before any data is received
        :raise SpinnmanIOException: If an error occurs receiving the data
        """
        try:
            self._socket.settimeout(timeout)
            return self._socket.recvfrom(300)
        except socket.timeout as e:
            raise_from(SpinnmanTimeoutException("receive", timeout), e)
        except Exception as e:  # pylint: disable=broad-except
            raise_from(SpinnmanIOException(str(e)), e)

    def send(self, data):
        """ Send data down this connection

        :param data: The data to be sent
        :type data: str
        :raise SpinnmanIOException: If there is an error sending the data
        """
        if not self._can_send:
            raise SpinnmanIOException(
                "Remote host and/or port not set - data cannot be sent with"
                " this connection")
        try:
            self._socket.send(data)
        except Exception as e:  # pylint: disable=broad-except
            raise_from(SpinnmanIOException(str(e)), e)

    def send_to(self, data, address):
        """ Send data down this connection

        :param data: The data to be sent as a bytestring
        :type data: str
        :param address: A tuple of (address, port) to send the data to
        :type address: (str, int)
        :raise SpinnmanIOException: If there is an error sending the data
        """
        try:
            self._socket.sendto(data, address)
        except Exception as e:  # pylint: disable=broad-except
            raise_from(SpinnmanIOException(str(e)), e)

    @overrides(Connection.close)
    def close(self):
        try:
            self._socket.shutdown(socket.SHUT_WR)
        except Exception:  # pylint: disable=broad-except
            pass
        self._socket.close()

    def is_ready_to_receive(self, timeout=0):
        return len(select.select([self._socket], [], [], timeout)[0]) == 1

    def __repr__(self):
        return _REPR_TEMPLATE.format(
            self.local_ip_address, self.local_port,
            self.remote_ip_address, self.remote_port)
