from spinnman.connections.abstract_sdp_sender import AbstractSDPSender
from spinnman.connections.abstract_sdp_receiver import AbstractSDPReceiver
from spinnman.connections.abstract_scp_sender import AbstractSCPSender
from spinnman.connections.abstract_scp_receiver import AbstractSCPReceiver
from spinnman.connections.abstract_spinnaker_boot_sender import AbstractSpinnakerBootSender
from spinnman.connections.abstract_spinnaker_boot_receiver import AbstractSpinnakerBootReceiver

from spinnman.exceptions import SpinnmanIOException
from spinnman.exceptions import SpinnmanTimeoutException
from spinnman.exceptions import SpinnmanInvalidParameterException
from spinnman.exceptions import SpinnmanInvalidPacketException
from spinnman.messages.sdp_message import SDPMessage
from spinnman.messages.scp_message import SCPMessage
from spinnman.messages.spinnaker_boot_message import SpinnakerBootMessage
from spinnman.messages.spinnaker_boot_message import BOOT_MESSAGE_VERSION

from spinnman._utils import _get_int_from_little_endian_bytearray
from spinnman._utils import _get_short_from_little_endian_bytearray
from spinnman._utils import _put_int_in_little_endian_byte_array
from spinnman._utils import _put_short_in_little_endian_byte_array
from spinnman._utils import _get_int_from_big_endian_bytearray
from spinnman._utils import _get_short_from_big_endian_bytearray
from spinnman._utils import _put_int_in_big_endian_byte_array
from spinnman._utils import _put_short_in_big_endian_byte_array

import platform
import subprocess
import socket


def _get_int_from_scp(array, offset):
    """ Wrapper function in case the endianness changes
    """
    return _get_int_from_little_endian_bytearray(array, offset)


def _get_short_from_scp(array, offset):
    """ Wrapper function in case the endianness changes
    """
    return _get_short_from_little_endian_bytearray(array, offset)


def _put_int_in_scp(array, offset, value):
    """ Wrapper function in case endianness changes
    """
    _put_int_in_little_endian_byte_array(array, offset, value)
    

def _put_short_in_scp(array, offset, value):
    """ Wrapper function in case endianness changes
    """
    _put_short_in_little_endian_byte_array(array, offset, value)


def _get_int_from_boot(array, offset):
    """ Wrapper function in case the endianness changes
    """
    return _get_int_from_big_endian_bytearray(array, offset)


def _get_short_from_boot(array, offset):
    """ Wrapper function in case the endianness changes
    """
    return _get_short_from_big_endian_bytearray(array, offset)


def _put_int_in_boot(array, offset, value):
    """ Wrapper function in case endianness changes
    """
    _put_int_in_big_endian_byte_array(array, offset, value)


def _put_short_in_boot(array, offset, value):
    """ Wrapper function in case endianness changes
    """
    _put_short_in_big_endian_byte_array(array, offset, value)


class UDPConnection(
        AbstractSDPSender, AbstractSDPReceiver,
        AbstractSCPSender, AbstractSCPReceiver,
        AbstractSpinnakerBootSender, AbstractSpinnakerBootReceiver):
    """ A connection to the spinnaker board that uses UDP to send and/or\
        receive data.  This supports SDP, SCP and SpiNNaker boot.  Note that\
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
            remote_port=17893, default_sdp_tag=0xFF):
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
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    setting up the communication channel
        """
        
        # Store the default sdp tag
        self._default_sdp_tag = default_sdp_tag
        
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
                self._remote_ip_address = socket.gethostbyname(
                        remote_host)
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
            if (platform.platform().lower().startswith("windows")):
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
    
    def _put_sdp_headers_into_message(self, packet, offset, sdp_message):
        """ Adds the headers of an SDP message into a packet buffer,
            applying defaults where the values have not been set
        
        :param packet: The packet buffer
        :type packet: bytearray
        :param offset: The offset in to the buffer where the headers should\
                    start
        :type offset: int
        :param sdp_message: The SDP message containing the header values
        :type sdp_message: :py:class:`spinnman.messages.sdp_message.SDPMessage`
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If the\
                    packet already has a source_port != 7, a source_cpu != 31,\
                    a source_chip_x != 0, or a source_chip_y != 0
        """
        tag = sdp_message.tag
        if tag is None:
            tag = self._default_sdp_tag
            
        if (sdp_message.source_port is not None
                and sdp_message.source_port != UDPConnection._SDP_SOURCE_PORT):
            raise SpinnmanInvalidParameterException(
                    "message.source_port", sdp_message.source_port,
                    "The source port must be {} to work with this connection"
                    .format(UDPConnection._SDP_SOURCE_PORT))
        
        if (sdp_message.source_cpu is not None
                and sdp_message.source_cpu != UDPConnection._SDP_SOURCE_CPU):
            raise SpinnmanInvalidParameterException(
                    "message.source_cpu", sdp_message.source_cpu,
                    "The source cpu must be {} to work with this connection"
                    .format(UDPConnection._SDP_SOURCE_CPU))
        
        if (sdp_message.source_chip_x is not None
                and sdp_message.source_chip_x
                        != UDPConnection._SDP_SOURCE_CHIP_X):
            raise SpinnmanInvalidParameterException(
                    "message.source_chip_x", sdp_message.source_chip_x,
                    "The source chip x must be {} to work with this connection"
                    .format(UDPConnection._SDP_SOURCE_CHIP_X))
        
        if (sdp_message.source_chip_y is not None
                and sdp_message.source_chip_y
                        != UDPConnection._SDP_SOURCE_CHIP_Y):
            raise SpinnmanInvalidParameterException(
                    "message.source_chip_y", sdp_message.source_chip_y,
                    "The source chip y must be {} to work with this connection"
                    .format(UDPConnection._SDP_SOURCE_CHIP_Y))
        
        packet[offset] = sdp_message.flags.value
        packet[offset + 1] = tag
        packet[offset + 2] = (((sdp_message.destination_port & 0x7) << 5) |
                               (sdp_message.destination_cpu & 0x1F))
        packet[offset + 3] = (((UDPConnection._SDP_SOURCE_PORT & 0x7) << 5) |
                               (UDPConnection._SDP_SOURCE_CPU & 0x1F))
        packet[offset + 4] = sdp_message.destination_chip_x
        packet[offset + 5] = sdp_message.destination_chip_y
        packet[offset + 6] = UDPConnection._SDP_SOURCE_CHIP_X
        packet[offset + 7] = UDPConnection._SDP_SOURCE_CHIP_Y

    def send_sdp_message(self, sdp_message):
        """ See :py:meth:`spinnman.connections.abstract_sdp_sender.AbstractSDPSender.send_sdp_message`
        
        tag is optional in the message - if not assigned, the default\
        specified in the constructor will be used.
        """
        if not self._can_send:
            raise SpinnmanIOException("Not connected to a remote host")
        
        # Create an array with the correct number of entries
        data_length = 0
        if sdp_message.data is not None:
            data_length = len(sdp_message.data)
        packet = bytearray(10 + data_length)
        
        # Add the UDP padding
        packet[0] = 0
        packet[1] = 0
        
        # Put all the message headers in to the packet
        self._put_sdp_headers_into_message(packet, 2, sdp_message)
        
        # Put the data in to the packet
        if data_length > 0:
            packet[10:] = sdp_message.data
        
        # Send the packet
        try:
            self._socket.send(packet)
        except Exception as e:
            raise SpinnmanIOException(str(e))
    
    def receive_sdp_message(self, timeout=None):
        """ See :py:meth:`spinnman.connections.abstract_sdp_receiver.AbstractSDPReceiver.receive_sdp_message`
        """
        
        # Receive the data
        raw_data = None
        try:
            self._socket.settimeout(timeout)
            raw_data = self._socket.recv(512)
        except socket.timeout:
            raise SpinnmanTimeoutException("receive_sdp_message", timeout)
        except Exception as e:
            raise SpinnmanIOException(str(e))
        
        # Parse the data
        packet = bytearray(raw_data)
        if len(packet) < 10:
            raise SpinnmanInvalidPacketException(
                    "SDP", "Only {} bytes of data received, but the minimum"
                    " for SDP is {}".format(len(packet), 10))
        data = None
        if len(packet) > 10:
            data = packet[10:]
            
        # Parse the header
        message = SDPMessage(
                flags=packet[2],
                tag=packet[3],
                destination_port=(packet[4] >> 5) & 0x7,
                destination_chip_x=packet[6],
                destination_chip_y=packet[7],
                destination_cpu=packet[4] & 0x1F,
                source_port=(packet[5] >> 5) & 0x7,
                source_chip_x=packet[8],
                source_chip_y=packet[9],
                source_cpu=packet[5] & 0x1F,
                data=data)
        return message
    
    def send_scp_message(self, scp_message):
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
        
        # Create an array with the correct number of entries
        data_length = 0
        if scp_message.data is not None:
            data_length = len(scp_message.data)
        packet = bytearray(26 + data_length)
        
        # Add the UDP padding
        packet[0] = 0
        packet[1] = 0
        
        # Put all the SDP message headers in to the packet
        self._put_sdp_headers_into_message(packet, 2, scp_message)

        # Work out the sequence number
        sequence = scp_message.sequence
        if sequence is None:
            sequence = self._scp_sequence
            self._scp_sequence = (self._scp_sequence + 1) % 65536
        
        # Put all the SCP message headers in to the packet (little-endian)
        _put_short_in_scp(packet, 10, scp_message.command.value)
        _put_short_in_scp(packet, 12, sequence)
        _put_int_in_scp(packet, 14, scp_message.argument_1)
        _put_int_in_scp(packet, 18, scp_message.argument_2)
        _put_int_in_scp(packet, 22, scp_message.argument_3)
        
        # Put the data in to the packet
        if data_length > 0:
            packet[26:] = scp_message.data
        
        # Send the packet
        try:
            self._socket.send(packet)
        except Exception as e:
            raise SpinnmanIOException(str(e))
    
    def receive_scp_message(self, timeout=None):
        """ See :py:meth:`spinnman.connections.abstract_scp_receiver.AbstractSCPReceiver.receive_scp_message`
        """
        
        # Receive the data
        raw_data = None
        try:
            self._socket.settimeout(timeout)
            raw_data = self._socket.recv(512)
        except socket.timeout:
            raise SpinnmanTimeoutException("receive_scp_message", timeout)
        except Exception as e:
            raise SpinnmanIOException(str(e))
        
        # Parse the data
        packet = bytearray(raw_data)
        if len(packet) < 26:
            raise SpinnmanInvalidPacketException(
                    "SCP", "Only {} bytes of data received, but the minimum"
                    " for SCP is {}".format(len(packet), 26))
        if len(packet) > 26 + 256:
            raise SpinnmanInvalidPacketException(
                    "SCP", "{} bytes of data received, but the maximum for SCP"
                    "is {}".format(len(packet), 26 + 256))
        data = None
        if len(packet) > 26:
            data = packet[26:]
            
        # Parse the header (little endian)
        message = SCPMessage(
                flags=packet[2],
                tag=packet[3],
                destination_port=(packet[4] >> 5) & 0x7,
                destination_chip_x=packet[6],
                destination_chip_y=packet[7],
                destination_cpu=packet[4] & 0x1F,
                source_port=(packet[5] >> 5) & 0x7,
                source_chip_x=packet[8],
                source_chip_y=packet[9],
                source_cpu=packet[5] & 0x1F,
                command=_get_short_from_scp(packet, 10),
                sequence=_get_short_from_scp(packet, 12),
                argument_1=_get_int_from_scp(packet, 14),
                argument_2=_get_int_from_scp(packet, 18),
                argument_3=_get_int_from_scp(packet, 22),
                data=data)
        return message
    
    def send_boot_message(self, boot_message):
        """ See :py:meth:`spinnman.connections.abstract_spinnaker_boot_sender.AbstractSpinnakerBootSender.send_boot_message`
        """
        if not self._can_send:
            raise SpinnmanIOException("Not connected to a remote host")
        
        # Create an array with the correct number of entries
        data_length = 0
        if boot_message.data is not None:
            data_length = len(boot_message.data)
        packet = bytearray(18 + data_length)
        
        # Put the headers into the message (big-endian)
        _put_short_in_boot(packet, 0, BOOT_MESSAGE_VERSION)
        _put_int_in_boot(packet, 2, boot_message.opcode.value)
        _put_int_in_boot(packet, 6, boot_message.operand_1)
        _put_int_in_boot(packet, 10, boot_message.operand_2)
        _put_int_in_boot(packet, 14, boot_message.operand_3)
        
        # Put the data in to the packet
        if data_length > 0:
            packet[18:] = boot_message.data
        
        # Send the packet
        try:
            self._socket.send(packet)
        except Exception as e:
            raise SpinnmanIOException(str(e))
    
    def receive_boot_message(self, timeout=None):
        """ See :py:meth:`spinnman.connections.abstract_spinnaker_boot_receiver.AbstractSpinnakerBootReceiver.receive_boot_message`
        """
        
        # Receive the data
        raw_data = None
        try:
            self._socket.settimeout(timeout)
            raw_data = self._socket.recv(2048)
        except socket.timeout:
            raise SpinnmanTimeoutException("receive_scp_message", timeout)
        except Exception as e:
            raise SpinnmanIOException(str(e))
        
        # Parse the data
        packet = bytearray(raw_data)
        if len(packet) < 18:
            raise SpinnmanInvalidPacketException(
                    "SpiNNaker Boot", "Only {} bytes of data received, but the"
                    " minimum for Boot packets is {}".format(len(packet), 18))
        if len(packet) > 18 + (256 * 4):
            raise SpinnmanInvalidPacketException(
                    "SpiNNaker Boot", "{} bytes of data received, but the"
                    " maximum for Boot packets is {}".format(len(packet),
                            18 + (256 * 4)))
        data = None
        if len(packet) > 18:
            data = packet[18:]
            
        # Check the version
        version = (packet[0] << 8) | packet[1]
        if version != 1:
            raise SpinnmanInvalidParameterException(
                    "boot message version", version,
                    "Only version 1 of the spinnaker boot protocol is"
                    " currently supported")
            
        # Parse the header (big endian)
        message = SpinnakerBootMessage(
                opcode=_get_int_from_boot(packet, 2),
                operand_1=_get_int_from_boot(packet, 6),
                operand_2=_get_int_from_boot(packet, 10),
                operand_3=_get_int_from_boot(packet, 14),
                data=data)
        return message
