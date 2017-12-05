from spinnman.exceptions \
    import SpinnmanIOException, SpinnmanTimeoutException
from spinnman.connections.abstract_classes import Connection

import logging
import platform
import subprocess
import socket
import select

logger = logging.getLogger(__name__)
_RECEIVE_BUFFER_SIZE = 1048576


class UDPConnection(Connection):
    @staticmethod
    def __get_socket():
        """Wrapper round socket() system call"""
        try:
            # Create a UDP Socket
            return socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except Exception as exception:
            raise SpinnmanIOException(
                "Error setting up socket: {}".format(exception))

    @staticmethod
    def __set_receive_buffer_size(sock, size):
        """Wrapper round setsockopt() system call"""
        try:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, size)
        except Exception:
            # The OS said no, but we might still be able to work right with
            # the defaults. Just warn and hope...
            logger.warn("failed to configure UDP socket to have a large "
                        "receive buffer", exc_info=True)

    @staticmethod
    def __bind_socket(sock, host, port):
        """Wrapper round bind() system call"""
        try:
            # Bind the socket
            sock.bind((str(host), int(port)))
        except Exception as exception:
            raise SpinnmanIOException(
                "Error binding socket to {}:{}: {}".format(
                    host, port, exception))

    @staticmethod
    def __resolve_host(host):
        """Wrapper round gethostbyname() system call"""
        try:
            return socket.gethostbyname(host)
        except Exception as exception:
            raise SpinnmanIOException(
                "Error getting ip address for {}: {}".format(
                    host, exception))

    @staticmethod
    def __connect_socket(sock, remote_address, remote_port):
        """Wrapper round connect() system call"""
        try:
            sock.connect((str(remote_address), int(remote_port)))
        except Exception as exception:
            raise SpinnmanIOException(
                "Error connecting to {}:{}: {}".format(
                    remote_address, remote_port, exception))

    @staticmethod
    def __get_socket_address(sock):
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

    def __init__(self, local_host=None, local_port=None, remote_host=None,
                 remote_port=None):
        """
        :param local_host: The local host name or ip address to bind to.\
            If not specified defaults to bind to all interfaces, unless\
            remote_host is specified, in which case binding is done to the\
            IP address that will be used to send packets
        :type local_host: str or None
        :param local_port: The local port to bind to, between 1025 and 65535.\
            If not specified, defaults to a random unused local port
        :type local_port: int
        :param remote_host: The remote host name or ip address to send packets\
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

        self._socket = self.__get_socket()
        self.__set_receive_buffer_size(self._socket, _RECEIVE_BUFFER_SIZE)

        # Get the host and port to bind to locally
        local_bind_host = "" if local_host is None else local_host
        local_bind_port = 0 if local_port is None else local_port
        self.__bind_socket(self._socket, local_bind_host, local_bind_port)

        # Mark the socket as non-sending, unless the remote host is
        # specified - send requests will then cause an exception
        self._can_send = False
        self._remote_ip_address = None
        self._remote_port = None

        # Get the host to connect to remotely
        if remote_host is not None and remote_port is not None:
            self._remote_port = remote_port
            self._remote_ip_address = self.__resolve_host(remote_host)
            self.__connect_socket(self._socket, self._remote_ip_address,
                                  remote_port)
            self._can_send = True

        # Get the details of where the socket is connected
        self._local_ip_address, self._local_port = \
            self.__get_socket_address(self._socket)

        # Set a general timeout on the socket
        self._socket.settimeout(1.0)

    def is_connected(self):
        """ See\
            :py:meth:`spinnman.connections.abstract_classes.connection.Connection.is_connected`
        """

        # If this is not a sending socket, it is not connected
        if not self._can_send:
            return False

        # check if machine is active and on the network
        pingtimeout = 5
        while pingtimeout > 0:
            # Start a ping process
            process = self._do_single_ping(self._remote_ip_address)
            if process.returncode == 0:
                # ping worked
                return True
            pingtimeout -= 1

        # If the ping fails this number of times, the host cannot be contacted
        return False

    @staticmethod
    def _do_single_ping(address):
        if platform.platform().lower().startswith("windows"):
            process = subprocess.Popen("ping -n 1 -w 1 " + address,
                                       shell=True, stdout=subprocess.PIPE)
        else:
            process = subprocess.Popen("ping -c 1 -W 1 " + address,
                                       shell=True, stdout=subprocess.PIPE)
        process.wait()
        return process

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
        except socket.timeout:
            raise SpinnmanTimeoutException("receive", timeout)
        except Exception as e:
            raise SpinnmanIOException(str(e))

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
        except socket.timeout:
            raise SpinnmanTimeoutException("receive", timeout)
        except Exception as e:
            raise SpinnmanIOException(str(e))

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
        except Exception as e:
            raise SpinnmanIOException(str(e))

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
        except Exception as e:
            raise SpinnmanIOException(str(e))

    def close(self):
        """ See\
            :py:meth:`spinnman.connections.abstract_classes.connection.Connection.close`
        """
        try:
            self._socket.shutdown(socket.SHUT_WR)
        except Exception:
            pass
        self._socket.close()

    def is_ready_to_receive(self, timeout=0):
        return len(select.select([self._socket], [], [], timeout)[0]) == 1

    def __repr__(self):
        return \
            "UDPConnection(local_host={}, local_port={}, remote_host={},"\
            "remote_port={})".format(
                self.local_ip_address, self.local_port,
                self.remote_ip_address, self.remote_port)
