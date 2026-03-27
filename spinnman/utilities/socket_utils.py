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
from typing import Optional, Tuple
from spinn_utilities.log import FormatAdapter
from spinnman.exceptions import SpinnmanIOException, SpinnmanTimeoutException

logger = FormatAdapter(logging.getLogger(__name__))


def get_udp_socket() -> socket.socket:
    """
    Wrapper round socket() system call to produce UDP/IPv4 sockets.

    :returns: A socket using the default values for UDP/IPv4 sockets.
    """
    try:
        # Create a UDP Socket
        return socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    except Exception as e:  # pylint: disable=broad-except
        raise SpinnmanIOException(
            f"Error setting up socket: {e}") from e


def get_tcp_socket() -> socket.socket:
    """
    Wrapper round socket() system call to produce TCP/IPv4 sockets.

    .. note::
        TCP sockets cannot be used to talk to a SpiNNaker board.

    :returns: A Socket using the default values for TCP/IPv4 sockets
    """
    try:
        # Create a UDP Socket
        return socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except Exception as e:  # pylint: disable=broad-except
        raise SpinnmanIOException(
            f"Error setting up socket: {e}") from e


# pylint: disable=wrong-spelling-in-docstring
def set_receive_buffer_size(sock: socket.socket, size: int) -> None:
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


def bind_socket(sock: socket.socket, host: str, port: int) -> None:
    """
    Wrapper round bind() system call.
    """
    try:
        # Bind the socket
        sock.bind((str(host), int(port)))
    except Exception as e:  # pylint: disable=broad-except
        raise SpinnmanIOException(
            f"Error binding socket to {host}:{port}: {e}") from e


def resolve_host(host: str) -> str:
    """
    Wrapper round gethostbyname() system call.

    :returns: host name in IPv4 address format
    """
    try:
        return socket.gethostbyname(host)
    except Exception as e:  # pylint: disable=broad-except
        raise SpinnmanIOException(
            f"Error getting IP address for {host}: {e}") from e


def connect_socket(
        sock: socket.socket, remote_address: str, remote_port: int) -> None:
    """
    Wrapper round connect() system call.
    """
    try:
        sock.connect((str(remote_address), int(remote_port)))
    except Exception as e:  # pylint: disable=broad-except
        raise SpinnmanIOException(
            f"Error connecting to {remote_address}:{remote_port}: {e}") from e


def get_socket_address(sock: socket.socket) -> Tuple[str, int]:
    """
    Wrapper round getsockname() system call.

    :returns: The urls and port
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


def receive_message(
        sock: socket.socket, timeout: Optional[float], size: int) -> bytes:
    """
    Wrapper round recv() system call.

    :returns: A bytes object representing the data received.
    """
    try:
        sock.settimeout(timeout)
        return sock.recv(size)
    except socket.timeout as e:
        raise SpinnmanTimeoutException("receive", timeout) from e
    except Exception as e:  # pylint: disable=broad-except
        raise SpinnmanIOException(f"Error receiving: {e}") from e


def receive_message_and_address(
        sock: socket.socket, timeout: Optional[float], size: int) -> Tuple[
            bytes, Tuple[str, int]]:
    """
    Wrapper round recvfrom() system call.

    :returns: the number of bytes sent
    """
    try:
        sock.settimeout(timeout)
        return sock.recvfrom(size)
    except socket.timeout as e:
        raise SpinnmanTimeoutException("receive", timeout) from e
    except Exception as e:  # pylint: disable=broad-except
        raise SpinnmanIOException(f"Error receiving: {e}") from e


def send_message(sock: socket.socket, data: bytes) -> int:
    """
    Wrapper round send() system call.

    :returns: Result of the socket call
    """
    try:
        return sock.send(data)
    except Exception as e:  # pylint: disable=broad-except
        raise SpinnmanIOException(f"Error sending: {e}") from e


def send_message_to_address(
        sock: socket.socket, data: bytes, address: Tuple[str, int]) -> int:
    """
    Wrapper round sendto() system call.

    :returns: Result of the socket call
    """
    try:
        return sock.sendto(data, address)
    except Exception as e:  # pylint: disable=broad-except
        raise SpinnmanIOException(f"Error sending: {e}") from e
