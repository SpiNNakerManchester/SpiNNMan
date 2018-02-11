import logging
import platform
import socket
import subprocess
from spinnman.exceptions import SpinnmanIOException

logger = logging.getLogger(__name__)
_SDP_SOURCE_PORT = 7
_SDP_SOURCE_CPU = 31
_SDP_TAG = 0xFF


def update_sdp_header_for_udp_send(sdp_header, source_x, source_y):
    """ Apply defaults to the sdp header for sending over UDP

    :param sdp_header: The SDP header values
    :type sdp_header:\
                :py:class:`spinnman.messages.sdp.sdp_header.SDPHeader`
    :return: Nothing is returned
    """
    sdp_header.tag = _SDP_TAG
    sdp_header.source_port = _SDP_SOURCE_PORT
    sdp_header.source_cpu = _SDP_SOURCE_CPU
    sdp_header.source_chip_x = source_x
    sdp_header.source_chip_y = source_y


def get_socket():
    """Wrapper round socket() system call"""
    try:
        # Create a UDP Socket
        return socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    except Exception as exception:
        raise SpinnmanIOException(
            "Error setting up socket: {}".format(exception))


def set_receive_buffer_size(sock, size):
    """Wrapper round setsockopt() system call"""
    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, size)
    except Exception:
        # The OS said no, but we might still be able to work right with
        # the defaults. Just warn and hope...
        logger.warn("failed to configure UDP socket to have a large "
                    "receive buffer", exc_info=True)


def bind_socket(sock, host, port):
    """Wrapper round bind() system call"""
    try:
        # Bind the socket
        sock.bind((str(host), int(port)))
    except Exception as exception:
        raise SpinnmanIOException(
            "Error binding socket to {}:{}: {}".format(
                host, port, exception))


def resolve_host(host):
    """Wrapper round gethostbyname() system call"""
    try:
        return socket.gethostbyname(host)
    except Exception as exception:
        raise SpinnmanIOException(
            "Error getting ip address for {}: {}".format(
                host, exception))


def connect_socket(sock, remote_address, remote_port):
    """Wrapper round connect() system call"""
    try:
        sock.connect((str(remote_address), int(remote_port)))
    except Exception as exception:
        raise SpinnmanIOException(
            "Error connecting to {}:{}: {}".format(
                remote_address, remote_port, exception))


def get_socket_address(sock):
    """Wrapper round getsockname() system call"""
    try:
        addr, port = sock.getsockname()
        # Ensure that a standard address is used for the INADDR_ANY
        # hostname
        if addr is None or addr == "":
            addr = "0.0.0.0"
        return addr, port
    except Exception as exception:
        raise SpinnmanIOException("Error querying socket: {}".format(
            exception))


def ping(address):
    if platform.platform().lower().startswith("windows"):
        cmd = "ping -n 1 -w 1 " + address
    else:
        cmd = "ping -c 1 -W 1 " + address
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    process.wait()
    return process
