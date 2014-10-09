from spinnman.connections.abstract_sdp_sender import AbstractSDPSender
from spinnman.connections.abstract_sdp_receiver import AbstractSDPReceiver
from spinnman.connections.abstract_scp_sender import AbstractSCPSender
from spinnman.connections.abstract_scp_receiver import AbstractSCPReceiver

from spinnman.exceptions import SpinnmanIOException
from spinnman.exceptions import SpinnmanTimeoutException
from spinnman.exceptions import SpinnmanInvalidParameterException
from spinnman.exceptions import SpinnmanInvalidPacketException
from spinnman.messages.sdp.sdp_message import SDPMessage
from spinnman.messages.sdp.sdp_header import SDPHeader
from spinnman.data.little_endian_byte_array_byte_reader \
    import LittleEndianByteArrayByteReader
from spinnman.data.little_endian_byte_array_byte_writer \
    import LittleEndianByteArrayByteWriter

from spinnman import constants

import platform
import subprocess
import socket
import select


class UDPConnection(
        AbstractSDPSender, AbstractSDPReceiver,
        AbstractSCPSender, AbstractSCPReceiver):
    """ A connection to the spinnaker board that uses UDP to send and/or\
        receive data.  This supports SDP and SCP.  Note that\
        SCP messages sent through this connection must have the following\
        properties:

            * source_port is None or 7
            * source_cpu is None or 31
            * source_chip_x is None or 0
            * source_chip_y is None or 0

        The tag of an SDP or SCP message can be assigned; if it is not, it\
        will have a default value assigned before being sent.
    """

    # Values defined for the source of an SDP packet over Ethernet
    _SDP_SOURCE_PORT = 7
    _SDP_SOURCE_CPU = 31
    _SDP_SOURCE_CHIP_X = 0
    _SDP_SOURCE_CHIP_Y = 0

    def __init__(self, local_host=None, local_port=None, remote_host=None,
                 remote_port=constants.UDP_CONNECTION_DEFAULT_PORT,
                 default_sdp_tag=0xFF, chip_x=0, chip_y=0):
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
        :param default_sdp_tag: The default tag to use with sdp packets sent\
                    via this connection that do not have a tag set
        :type default_sdp_tag: int
        :param chip_x: The x-coordinate of the chip to which this connection\
                    is connected
        :type chip_x: int
        :param chip_y: The y-coordinate of the chip to which this connection\
                    is connected
        :type chip_y: int
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    setting up the communication channel
        """

        # Store the default sdp tag
        self._default_sdp_tag = default_sdp_tag

        # Store the chip coordinates
        self._chip_x = chip_x
        self._chip_y = chip_y

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

    def _update_sdp_header(self, sdp_header):
        """ Apply defaults to the sdp header where the values have not been set

        :param sdp_header: The SDP header values
        :type sdp_header:\
                    :py:class:`spinnman.messages.sdp.sdp_header.SDPHeader`
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If the\
                    packet already has a source_port != 7, a source_cpu != 31,\
                    a source_chip_x != 0, or a source_chip_y != 0
        """
        if sdp_header.tag is None:
            sdp_header.tag = self._default_sdp_tag

        if sdp_header.source_port is not None:
            if sdp_header.source_port != UDPConnection._SDP_SOURCE_PORT:
                raise SpinnmanInvalidParameterException(
                    "message.source_port", str(sdp_header.source_port),
                    "The source port must be {} to work with this"
                    " connection".format(UDPConnection._SDP_SOURCE_PORT))
        else:
            sdp_header.source_port = UDPConnection._SDP_SOURCE_PORT

        if sdp_header.source_cpu is not None:
            if sdp_header.source_cpu != UDPConnection._SDP_SOURCE_CPU:
                raise SpinnmanInvalidParameterException(
                    "message.source_cpu", str(sdp_header.source_cpu),
                    "The source cpu must be {} to work with this"
                    " connection".format(UDPConnection._SDP_SOURCE_CPU))
        else:
            sdp_header.source_cpu = UDPConnection._SDP_SOURCE_CPU

        if sdp_header.source_chip_x is not None:
            if sdp_header.source_chip_x != UDPConnection._SDP_SOURCE_CHIP_X:
                raise SpinnmanInvalidParameterException(
                    "message.source_chip_x", str(sdp_header.source_chip_x),
                    "The source chip x must be {} to work with this"
                    " connection".format(UDPConnection._SDP_SOURCE_CHIP_X))
        else:
            sdp_header.source_chip_x = UDPConnection._SDP_SOURCE_CHIP_X

        if sdp_header.source_chip_y is not None:
            if sdp_header.source_chip_y != UDPConnection._SDP_SOURCE_CHIP_Y:
                raise SpinnmanInvalidParameterException(
                    "message.source_chip_y", str(sdp_header.source_chip_y),
                    "The source chip y must be {} to work with this"
                    " connection".format(UDPConnection._SDP_SOURCE_CHIP_Y))
        else:
            sdp_header.source_chip_y = UDPConnection._SDP_SOURCE_CHIP_Y

    def send_sdp_message(self, sdp_message):
        """ See :py:meth:`spinnman.connections.abstract_sdp_sender.AbstractSDPSender.send_sdp_message`

        tag is optional in the message - if not assigned, the default\
        specified in the constructor will be used.
        """
        if not self._can_send:
            raise SpinnmanIOException("Not connected to a remote host")

        # Update the SDP headers for this connection
        self._update_sdp_header(sdp_message.sdp_header)

        # Create a writer for the mesage
        data_length = 0
        if sdp_message.data is not None:
            data_length = len(sdp_message.data)
        writer = LittleEndianByteArrayByteWriter()

        # Add the UDP padding
        writer.write_short(0)

        # Write the header
        sdp_message.sdp_header.write_sdp_header(writer)

        # Write any data
        if data_length != 0:
            writer.write_bytes(sdp_message.data)

        # Send the packet
        try:
            self._socket.send(writer.data)
        except Exception as e:
            raise SpinnmanIOException(str(e))

    def send_raw(self, message):
        """
        sends a raw udp packet
        :param message: the message sent in the udp packet

        :return: None
        """
        # Send the packet
        try:
            self._socket.send(message)
        except Exception as e:
            raise SpinnmanIOException(str(e))

    def send_eieio_message(self, eieio_message):
        """
        sends a eieio message in a udp packet
        :param eieio_message: the message sent in the udp packet
        :return:
        """
        if not self._can_send:
            raise SpinnmanIOException("Not connected to a remote host")

        # Create a writer for the message
        data_length = 0
        if eieio_message.data is not None:
            data_length = len(eieio_message.data)
        writer = LittleEndianByteArrayByteWriter()

        # Write the header
        eieio_message.eieio_header.write_eieio_header(writer)

        # Write any data
        if data_length != 0:
            writer.write_bytes(eieio_message.data)

        # Send the packet
        try:
            self._socket.send(writer.data)
        except Exception as e:
            raise SpinnmanIOException(str(e))

    def receive_sdp_message(self, timeout=None):
        """ See :py:meth:`spinnman.connections.abstract_sdp_receiver.AbstractSDPReceiver.receive_sdp_message`
        """

        # Receive the data
        raw_data = None
        try:
            read_ready, _, _ = select.select([self._socket], [], [], timeout)
            if not read_ready:
                raise socket.timeout()
            raw_data = self._socket.recv(512)
        except socket.timeout:
            raise SpinnmanTimeoutException("receive_sdp_message", timeout)
        except Exception as e:
            raise SpinnmanIOException(str(e))

        # Set up for reading
        packet = bytearray(raw_data)
        reader = LittleEndianByteArrayByteReader(packet)

        # Read the padding
        try:
            reader.read_short()
        except EOFError:
            raise SpinnmanInvalidPacketException(
                "SDP", "Not enough bytes to read the pre-packet padding")

        # Read the header and data
        sdp_header = SDPHeader()
        sdp_header.read_sdp_header(reader)
        data = reader.read_bytes()
        if len(data) == 0:
            data = None

        # Create and return the message
        message = SDPMessage(sdp_header=sdp_header, data=data)
        return message

    def send_scp_request(self, scp_request):
        """ See :py:meth:`spinnman.connections.abstract_scp_sender.AbstractSCPSender.send_scp_message`

        Messages must have the following properties:

            * source_port is None or 7
            * source_cpu is None or 31
            * source_chip_x is None or 0
            * source_chip_y is None or 0

        tag in the message is optional - if not set the default set in the\
        constructor will be used.
        sequence in the message is optional - if not set (sequence number\
        last assigned + 1) % 65536 will be used
        """
        if not self._can_send:
            raise SpinnmanIOException("Not connected to a remote host")

        # Update the SDP headers for this connection
        self._update_sdp_header(scp_request.sdp_header)

        # Update the sequence for this connection
        if scp_request.scp_request_header.sequence is None:
            scp_request.scp_request_header.sequence = self._scp_sequence
            self._scp_sequence = (self._scp_sequence + 1) % 65536

        # Create a writer for the mesage
        writer = LittleEndianByteArrayByteWriter()

        # Add the UDP padding
        writer.write_short(0)

        # Write the SCP message
        scp_request.write_scp_request(writer)

        # Send the packet
        try:
            self._socket.send(writer.data)
        except Exception as e:
            raise SpinnmanIOException(str(e))

    def receive_scp_response(self, scp_response, timeout=None):
        """ See :py:meth:`spinnman.connections.abstract_scp_receiver.AbstractSCPReceiver.receive_scp_message`
        """

        # Receive the data
        raw_data = None
        try:
            ready_read, _, _ = select.select([self._socket], [], [], timeout)
            if not ready_read:
                raise socket.timeout()
            raw_data = self._socket.recv(512)
        except socket.timeout:
            raise SpinnmanTimeoutException("receive_scp_message", timeout)
        except Exception as e:
            raise SpinnmanIOException(str(e))

        # Set up for reading
        packet = bytearray(raw_data)
        reader = LittleEndianByteArrayByteReader(packet)

        # Read the padding
        try:
            reader.read_short()
        except EOFError:
            raise SpinnmanInvalidPacketException(
                "SCP", "Not enough bytes to read the pre-packet padding")

        # Read the response
        scp_response.read_scp_response(reader)

    def close(self):
        """ See :py:meth:`spinnman.connections.abstract_connection.AbstractConnection.close`
        """
        self._socket.close()

    @property
    def chip_x(self):
        """ The x-coordinate of the chip with the ethernet connection to\
            which all packets will be sent

        :rtype: int
        """
        return self._chip_x

    @property
    def chip_y(self):
        """ The y-coordinate of the chip with the ethernet connection to\
            which all packets will be sent

        :rtype: int
        """
        return self._chip_y
