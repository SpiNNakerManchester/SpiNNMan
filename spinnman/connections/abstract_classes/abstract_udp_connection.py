from spinnman import constants
from spinnman.exceptions import SpinnmanIOException

from abc import ABCMeta
from abc import abstractmethod
from six import add_metaclass

import platform
import subprocess
import socket


@add_metaclass(ABCMeta)
class AbstractUDPConnection(object):

    def __init__(self, local_host=None, local_port=None, remote_host=None,
                 remote_port=constants.SCP_SCAMP_PORT):
        """
        :param local_host: The local host name or ip address to bind to.\
                    If not specified defaults to bind to all interfaces,\
                    unless remote_host is specified, in which case binding is\
                    _done to the ip address that will be used to send packets
        :type local_host: str
        :param local_port: The local port to bind to, between 1025 and 65535.\
                    If not specified, defaults to a random unused local port
        :type local_port: int
        :param remote_host: The remote host name or ip address to send packets\
                    to.  If not specified, the socket will be available for\
                    listening only, and will throw and exception if used for\
                    sending
        :type remote_host: str
        :param remote_port: The remote port to send packets to.  If\
                    remote_host is None, this is ignored.
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    setting up the communication channel
        """

        # Keep track of the current scp sequence number
        self._scp_sequence = 0

        self._socket = None
        try:

            # Create a UDP Socket
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        except Exception as exception:
            raise SpinnmanIOException(
                "Error setting up socket: {}".format(exception))

        # Get the port to bind to locally
        local_bind_port = 0
        if local_port is not None:
            local_bind_port = int(local_port)

        # Get the host to bind to locally
        local_bind_host = ""
        if local_host is not None:
            local_bind_host = str(local_host)

        try:
            # Bind the socket
            self._socket.bind((local_bind_host, local_bind_port))

        except Exception as exception:
            raise SpinnmanIOException(
                "Error binding socket to {}:{}: {}".format(
                    local_bind_host, local_bind_port, exception))

        # Mark the socket as non-sending, unless the remote host is
        # specified - send requests will then cause an exception
        self._can_send = False
        self._remote_ip_address = None
        self._remote_port = None

        # Get the host to connect to remotely
        if remote_host is not None:
            self._can_send = True
            self._remote_port = remote_port

            try:
                self._remote_ip_address = socket.gethostbyname(remote_host)
            except Exception as exception:
                raise SpinnmanIOException(
                    "Error getting ip address for {}: {}".format(
                        remote_host, exception))

            try:
                self._socket.connect((self._remote_ip_address, remote_port))
            except Exception as exception:
                raise SpinnmanIOException(
                    "Error connecting to {}:{}: {}".format(
                        self._remote_ip_address, remote_port, exception))

        # Get the details of where the socket is connected
        self._local_ip_address = None
        self._local_port = None
        try:
            self._local_ip_address, self._local_port =\
                self._socket.getsockname()
        except Exception as exception:
            raise SpinnmanIOException("Error querying socket: {}".format(
                exception))

        # Set a general timeout on the socket
        self._socket.settimeout(1.0)
        self._socket.setblocking(0)

    def is_connected(self):
        """ See :py:meth:`spinnman.connections.AbstractConnection.abstract_connection.is_connected`
        """

        # If this is not a sending socket, it is not connected
        if not self._can_send:
            return False

        # check if machine is active and on the network
        pingtimeout = 5
        while pingtimeout > 0:

            # Start a ping process
            process = None
            if platform.platform().lower().startswith("windows"):
                process = subprocess.Popen(
                    "ping -n 1 -w 1 " + self._remote_ip_address,
                    shell=True, stdout=subprocess.PIPE)
            else:
                process = subprocess.Popen(
                    "ping -c 1 -W 1 " + self._remote_ip_address,
                    shell=True, stdout=subprocess.PIPE)
            process.wait()

            if process.returncode == 0:

                # ping worked
                return True
            else:
                pingtimeout -= 1

        # If the ping fails this number of times, the host cannot be contacted
        return False

    @property
    def local_ip_address(self):
        """ The local IP address to which the connection is bound.

        :return: The local ip address as a dotted string e.g. 0.0.0.0
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
        """ The remote ip address to which the connection is connected.

        :return: The remote ip address as a dotted string, or None if not\
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

    def close(self):
        """ See :py:meth:`spinnman.connections.abstract_connection.AbstractConnection.close`
        """
        self._socket.close()

    @property
    def can_send(self):
        """a helper property method to check if this connection can send

        :return:
        """
        return self._can_send

    @abstractmethod
    def connection_type(self):
        """
        method to help identify the connection
        :return:
        """

    @abstractmethod
    def supports_sends_message(self, message):
        """helper method to verify if the connection can deal with this message
        format

        :param message:
        :return:
        """
