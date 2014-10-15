from spinnman.connections.abstract_spinnaker_boot_sender \
    import AbstractSpinnakerBootSender
from spinnman.connections.abstract_spinnaker_boot_receiver \
    import AbstractSpinnakerBootReceiver

from spinnman.exceptions import SpinnmanIOException
from spinnman.exceptions import SpinnmanTimeoutException
from spinnman.exceptions import SpinnmanInvalidParameterException
from spinnman.exceptions import SpinnmanInvalidPacketException
from spinnman.messages.spinnaker_boot.spinnaker_boot_message \
    import SpinnakerBootMessage
from spinnman.messages.spinnaker_boot.spinnaker_boot_message \
    import BOOT_MESSAGE_VERSION
from spinnman.messages.spinnaker_boot.spinnaker_boot_op_code \
    import SpinnakerBootOpCode
from spinnman.data.big_endian_byte_array_byte_reader \
    import BigEndianByteArrayByteReader
from spinnman.data.big_endian_byte_array_byte_writer \
    import BigEndianByteArrayByteWriter
from spinnman import constants

import platform
import subprocess
import socket
import select


class UDPBootConnection(
        AbstractSpinnakerBootSender, AbstractSpinnakerBootReceiver):
    """ A connection to the spinnaker board that uses UDP to for booting
    """

    def __init__(self, local_host=None, local_port=None, remote_host=None,
                 remote_port=constants.UDP_BOOT_CONNECTION_DEFAULT_PORT):
        """
        :param local_host: The local host name or ip address to bind to.\
                    If not specified defaults to bind to all interfaces,\
                    unless remote_host is specified, in which case binding is\
                    done to the ip address that will be used to send packets
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

    def send_boot_message(self, boot_message):
        """ See :py:meth:`spinnman.connections.abstract_spinnaker_boot_sender.AbstractSpinnakerBootSender.send_boot_message`
        """
        if not self._can_send:
            raise SpinnmanIOException("Not connected to a remote host")

        # Create a writer for the mesage
        data_length = 0
        if boot_message.data is not None:
            data_length = len(boot_message.data)
        writer = BigEndianByteArrayByteWriter()

        # Put the headers into the message (big-endian)
        writer.write_short(BOOT_MESSAGE_VERSION)
        writer.write_int(boot_message.opcode.value)
        writer.write_int(boot_message.operand_1)
        writer.write_int(boot_message.operand_2)
        writer.write_int(boot_message.operand_3)

        # Put the data in to the packet
        if data_length > 0:
            writer.write_bytes(boot_message.data)

        # Send the packet
        try:
            self._socket.send(writer.data)
        except Exception as e:
            raise SpinnmanIOException(str(e))

    def receive_boot_message(self, timeout=None):
        """ See :py:meth:`spinnman.connections.abstract_spinnaker_boot_receiver.AbstractSpinnakerBootReceiver.receive_boot_message`
        """

        # Receive the data
        raw_data = None
        try:
            read_ready, _, _ = select.select([self._socket], [], [], timeout)
            if not read_ready:
                raise socket.timeout()
            raw_data = self._socket.recv(2048)
        except socket.timeout:
            raise SpinnmanTimeoutException("receive_scp_message", timeout)
        except Exception as e:
            raise SpinnmanIOException(str(e))

        # Create a reader
        packet = bytearray(raw_data)
        reader = BigEndianByteArrayByteReader(packet)

        opcode_value = None
        try:
            # Check the version
            version = reader.read_short()
            if version != 1:
                raise SpinnmanInvalidParameterException(
                    "boot message version", version,
                    "Only version 1 of the spinnaker boot protocol is"
                    " currently supported")

            # Read the values
            opcode_value = reader.read_int()
            opcode = SpinnakerBootOpCode(opcode_value)
            operand_1 = reader.read_int()
            operand_2 = reader.read_int()
            operand_3 = reader.read_int()
            data = reader.read_bytes()
            if len(data) == 0:
                data = None

            # Parse the header (big endian)
            message = SpinnakerBootMessage(
                opcode=opcode, operand_1=operand_1, operand_2=operand_2,
                operand_3=operand_3, data=data)
            return message
        except IOError as exception:
            raise SpinnmanIOException(str(exception))
        except EOFError:
            raise SpinnmanInvalidPacketException(
                "Boot", "Not enough bytes in the packet")
        except ValueError:
            raise SpinnmanInvalidParameterException(
                "opcode", opcode_value, "Unrecognized value")

    def close(self):
        """ See :py:meth:`spinnman.connections.abstract_connection.AbstractConnection.close`
        """
        self._socket.close()
