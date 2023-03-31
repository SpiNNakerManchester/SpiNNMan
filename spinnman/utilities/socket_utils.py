# Copyright (c) 2017 The University of Manchester
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
Wrappers around socket-related system calls to do exception remapping and
apply some consistency to things.
"""

import logging
import socket
from spinn_utilities.log import FormatAdapter
from spinnman.exceptions import SpinnmanIOException, SpinnmanTimeoutException

logger = FormatAdapter(logging.getLogger(__name__))


def get_udp_socket():
    """
    Wrapper round socket() system call to produce UDP/IPv4 sockets.
    """
    try:
        # Create a UDP Socket
        return socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    except Exception as e:  # pylint: disable=broad-except
        raise SpinnmanIOException(
            f"Error setting up socket: {e}") from e


def get_tcp_socket():
    """
    Wrapper round socket() system call to produce TCP/IPv4 sockets.

    .. note::
        TCP sockets cannot be used to talk to a SpiNNaker board.
    """
    try:
        # Create a UDP Socket
        return socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except Exception as e:  # pylint: disable=broad-except
        raise SpinnmanIOException(
            f"Error setting up socket: {e}") from e


def set_receive_buffer_size(sock, size):
    """
    Wrapper round setsockopt() system call.
    """
    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, size)
    except Exception:  # pylint: disable=broad-except
        # The OS said no, but we might still be able to work right with
        # the defaults. Just warn and hope...
        logger.warning("failed to configure UDP socket to have a large "
                       "receive buffer", exc_info=True)


def bind_socket(sock, host, port):
    """
    Wrapper round bind() system call.
    """
    try:
        # Bind the socket
        sock.bind((str(host), int(port)))
    except Exception as e:  # pylint: disable=broad-except
        raise SpinnmanIOException(
            f"Error binding socket to {host}:{port}: {e}") from e


def resolve_host(host):
    """
    Wrapper round gethostbyname() system call.
    """
    try:
        return socket.gethostbyname(host)
    except Exception as e:  # pylint: disable=broad-except
        raise SpinnmanIOException(
            f"Error getting IP address for {host}: {e}") from e


def connect_socket(sock, remote_address, remote_port):
    """
    Wrapper round connect() system call.
    """
    try:
        sock.connect((str(remote_address), int(remote_port)))
    except Exception as e:  # pylint: disable=broad-except
        raise SpinnmanIOException(
            f"Error connecting to {remote_address}:{remote_port}: {e}") from e


def get_socket_address(sock):
    """
    Wrapper round getsockname() system call.
    """
    try:
        addr, port = sock.getsockname()
        # Ensure that a standard address is used for the INADDR_ANY
        # hostname
        if addr is None or addr == "":
            addr = "0.0.0.0"
        return addr, port
    except Exception as e:  # pylint: disable=broad-except
        raise SpinnmanIOException(f"Error querying socket: {e}") from e


def receive_message(sock, timeout, size):
    """
    Wrapper round recv() system call.
    """
    try:
        sock.settimeout(timeout)
        return sock.recv(size)
    except socket.timeout as e:
        raise SpinnmanTimeoutException("receive", timeout) from e
    except Exception as e:  # pylint: disable=broad-except
        raise SpinnmanIOException(f"Error receiving: {e}") from e


def receive_message_and_address(sock, timeout, size):
    """
    Wrapper round recvfrom() system call.
    """
    try:
        sock.settimeout(timeout)
        return sock.recvfrom(size)
    except socket.timeout as e:
        raise SpinnmanTimeoutException("receive", timeout) from e
    except Exception as e:  # pylint: disable=broad-except
        raise SpinnmanIOException(f"Error receiving: {e}") from e


def send_message(sock, data):
    """
    Wrapper round send() system call.
    """
    try:
        return sock.send(data)
    except Exception as e:  # pylint: disable=broad-except
        raise SpinnmanIOException(f"Error sending: {e}") from e


def send_message_to_address(sock, data, address):
    """
    Wrapper round sendto() system call.
    """
    try:
        return sock.sendto(data, address)
    except Exception as e:  # pylint: disable=broad-except
        raise SpinnmanIOException(f"Error sending: {e}") from e
