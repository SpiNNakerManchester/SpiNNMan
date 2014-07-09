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

import platform
import subprocess
import socket

class UDPConnection(
        AbstractSDPSender, AbstractSDPReceiver, 
        AbstractSCPSender, AbstractSCPReceiver,
        AbstractSpinnakerBootSender, AbstractSpinnakerBootReceiver):
    """ A connection to the spinnaker board that uses UDP to send and/or\
        receive data
    """
    
    def __init__(self, local_host=None, local_port=None, remote_host=None,
            remote_port=17893):
        """
        :param local_host: The local host name or ip address to bind to.\
                    If not specified defaults to bind to all interfaces, unless\
                    remote_host is specified, in which case binding is done to\
                    the ip address that will be used to send packets
        :type local_host: str
        :param local_port: The local port to bind to, between 1025 and 65535.\
                    If not specified, defaults to a random unused local port
        :type local_port: int
        :param remote_host: The remote host name or ip address to send packets\
                    to.  If not specified, the socket will be available for\
                    listening only, and will throw and exception if used for\
                    sending
        :type remote_host: str
        :param remote_port: The remote port to send packets to.  If remote_host\
                    is None, this is ignored.
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    setting up the communication channel
        """
        
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
            
        # Get the host to connect to remotely
        remote_connect_host = None
        if remote_host is not None:
            self._can_send = True
            
            # Change connections to localhost to actually connect to
            # the local hostname
            if (remote_host.lower() in ('localhost', '127.0.0.1')):
                
                try:
                    remote_connect_host = socket.gethostname()
                except Exception as exception:
                    raise SpinnmanIOException(
                            "Error getting local hostname: {}".format(
                                    exception))
                
            connection_address = None
            try:
                self._remote_ip_address = socket.gethostbyname(
                        remote_connect_host)
            except Exception as exception:
                raise SpinnmanIOException(
                        "Error getting ip address for {}: {}".format(
                                remote_connect_host, exception))
            
            try:
                self._socket.connect((self._remote_ip_address, remote_port))
            except Exception as exception:
                raise SpinnmanIOException(
                        "Error connecting to {}:{}: {}".format(
                                connection_address, remote_port, exception))
        
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
        pingtimeout=5
        while pingtimeout > 0:
            
            # Start a ping process
            process = None
            if (platform.platform().lower().startswith("windows")):
                process = subprocess.Popen(
                        "ping -n 1 -w 1 " + self._remote_ip_address, shell=True,
                        stdout=subprocess.PIPE)
            else:
                process = subprocess.Popen(
                        "ping -c 1 -W 1 " + self._remote_ip_address, shell=True,
                        stdout=subprocess.PIPE)
            process.wait()
            
            if process.returncode == 0:
                
                # ping worked
                return True
            else:
                pingtimeout-=1
            
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

    def send_sdp_message(self, sdp_message):
        """ See :py:meth:`spinnman.connections.abstract_sdp_sender.AbstractSDPSender.send_sdp_message`
        """
        # Create an array with the correct number of entries
        data_length = 0
        if sdp_message.data is not None:
            data_length = len(sdp_message.data)
        packet = bytearray(10 + data_length)
        
        # Add the UDP padding
        packet[0] = 0
        packet[1] = 0
        
        # Put all the message headers in to the packet
        packet[2] = sdp_message.flags
        packet[3] = sdp_message.tag
        packet[4] = (((sdp_message.destination_port & 0x7) << 5) |
                (sdp_message.destination_cpu & 0x1F)) 
        packet[5] = (((sdp_message.source_port & 0x7) << 5) |
                (sdp_message.source_cpu & 0x1F))
        packet[6] = sdp_message.destination_chip_x
        packet[7] = sdp_message.destination_chip_y
        packet[8] = sdp_message.source_chip_x
        packet[9] = sdp_message.source_chip_y
        
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
            raw_data, _ = self._socket.recv(512)
        except socket.timeout:
            raise SpinnmanTimeoutException("receive_sdp_message", timeout)
        except Exception as e:
            raise SpinnmanIOException(str(e))
        
        # Parse the data
        packet = bytearray(raw_data)
        if len(packet) < 10:
            raise SpinnmanInvalidPacketException(
                    "SDP", "Only {} bytes of data received, but the minimum for"
                    " SDP is {}".format(len(packet), 10))
        data = None
        if len(packet) > 10:
            data = packet[10:]
            
        # Parse the header
        message = SDPMessage(
                flags = packet[2], 
                tag = packet[3], 
                destination_port = (packet[4] >> 5) & 0x7, 
                destination_chip_x = packet[6], 
                destination_chip_y = packet[7],
                destination_cpu = packet[4] & 0x1F, 
                source_port = (packet[5] >> 5) & 0x7, 
                source_chip_x = packet[8], 
                source_chip_y = packet[9], 
                source_cpu = packet[5] & 0x1F, 
                data = data)
        return message
    
    def send_scp_message(self, scp_message):
        """ See :py:meth:`spinnman.connections.abstract_scp_sender.AbstractSCPSender.send_scp_message`
        """
        # Create an array with the correct number of entries
        data_length = 0
        if scp_message.data is not None:
            data_length = len(scp_message.data)
        packet = bytearray(26 + data_length)
        
        # Add the UDP padding
        packet[0] = 0
        packet[1] = 0
        
        # Put all the SDP message headers in to the packet
        packet[2] = scp_message.flags
        packet[3] = scp_message.tag
        packet[4] = (((scp_message.destination_port & 0x7) << 5) |
                (scp_message.destination_cpu & 0x1F)) 
        packet[5] = (((scp_message.source_port & 0x7) << 5) |
                (scp_message.source_cpu & 0x1F))
        packet[6] = scp_message.destination_chip_x
        packet[7] = scp_message.destination_chip_y
        packet[8] = scp_message.source_chip_x
        packet[9] = scp_message.source_chip_y
        
        # Put all the SCP message headers in to the packet (little-endian)
        packet[10] = scp_message.cmd & 0xFF
        packet[11] = (scp_message.cmd >> 8) & 0xFF
        packet[12] = scp_message.sequence & 0xFF
        packet[13] = (scp_message.sequence >> 8) & 0xFF
        packet[14] = scp_message.arg1 & 0xFF
        packet[15] = (scp_message.arg1 >> 8) & 0xFF
        packet[16] = (scp_message.arg1 >> 16) & 0xFF
        packet[17] = (scp_message.arg1 >> 24) & 0xFF
        packet[18] = scp_message.arg2 & 0xFF
        packet[19] = (scp_message.arg2 >> 8) & 0xFF
        packet[20] = (scp_message.arg2 >> 16) & 0xFF
        packet[21] = (scp_message.arg2 >> 24) & 0xFF
        packet[22] = scp_message.arg3 & 0xFF
        packet[23] = (scp_message.arg3 >> 8) & 0xFF
        packet[24] = (scp_message.arg3 >> 16) & 0xFF
        packet[25] = (scp_message.arg3 >> 24) & 0xFF
        
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
            raw_data, _ = self._socket.recv(512)
        except socket.timeout:
            raise SpinnmanTimeoutException("receive_scp_message", timeout)
        except Exception as e:
            raise SpinnmanIOException(str(e))
        
        # Parse the data
        packet = bytearray(raw_data)
        if len(packet) < 26:
            raise SpinnmanInvalidPacketException(
                    "SCP", "Only {} bytes of data received, but the minimum for"
                    " SCP is {}".format(len(packet), 26))
        if len(packet) > 26 + 256:
            raise SpinnmanInvalidPacketException(
                    "SCP", "{} bytes of data received, but the maximum for SCP"
                    "is {}".format(len(packet), 26 + 256))
        data = None
        if len(packet) > 26:
            data = packet[26:]
            
        # Parse the header (little endian)
        message = SCPMessage(flags = packet[2], 
                tag = packet[3], 
                destination_port = (packet[4] >> 5) & 0x7, 
                destination_chip_x = packet[6], 
                destination_chip_y = packet[7],
                destination_cpu = packet[4] & 0x1F, 
                source_port = (packet[5] >> 5) & 0x7, 
                source_chip_x = packet[8], 
                source_chip_y = packet[9], 
                source_cpu = packet[5] & 0x1F, 
                command = (packet[11] << 8) | packet[10], 
                sequence = (packet[13] << 8) | packet[12], 
                argument_1 = ((packet[17] << 24) | (packet[16] << 16) 
                        | (packet[15] << 8) | packet[14]), 
                argument_2 = ((packet[21] << 24) | (packet[20] << 16) 
                        | (packet[19] << 8) | packet[18]), 
                argument_3 = ((packet[25] << 24) | (packet[24] << 16) 
                        | (packet[23] << 8) | packet[22]), 
                data = data)
        return message
    
    def send_boot_message(self, boot_message):
        """ See :py:meth:`spinnman.connections.abstract_spinnaker_boot_sender.AbstractSpinnakerBootSender.send_boot_message`
        """
        # Create an array with the correct number of entries
        data_length = 0
        if boot_message.data is not None:
            data_length = len(boot_message.data)
        packet = bytearray(18 + data_length)
        
        # Put the headers into the message (big-endian)
        opcode = boot_message.opcode.value()
        packet[0] = (boot_message.version >> 8) & 0xFF
        packet[1] = boot_message.version & 0xFF
        packet[2] = (opcode >> 24) & 0xFF
        packet[3] = (opcode >> 16) & 0xFF
        packet[4] = (opcode >> 8) & 0xFF
        packet[5] = opcode & 0xFF
        packet[6] = (boot_message.operand_1 >> 24) & 0xFF
        packet[7] = (boot_message.operand_1 >> 16) & 0xFF
        packet[8] = (boot_message.operand_1 >> 8) & 0xFF
        packet[9] = boot_message.operand_1 & 0xFF
        packet[10] = (boot_message.operand_2 >> 24) & 0xFF
        packet[11] = (boot_message.operand_2 >> 16) & 0xFF
        packet[12] = (boot_message.operand_2 >> 8) & 0xFF
        packet[13] = boot_message.operand_2 & 0xFF
        packet[14] = (boot_message.operand_3 >> 24) & 0xFF
        packet[15] = (boot_message.operand_3 >> 16) & 0xFF
        packet[16] = (boot_message.operand_3 >> 8) & 0xFF
        packet[17] = boot_message.operand_3 & 0xFF
        
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
            raw_data, _ = self._socket.recv(2048)
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
                    "Only version 1 of the spinnaker boot protocol is currently"
                    " supported")
            
        # Parse the header (big endian)
        message = SpinnakerBootMessage(
                opcode = ((packet[2] << 24) | (packet[3] << 16) 
                        | (packet[4] << 8) | packet[5]), 
                operand_1 = ((packet[6] << 24) | (packet[7] << 16) 
                        | (packet[8] << 8) | packet[9]), 
                operand_2 = ((packet[10] << 24) | (packet[11] << 16) 
                        | (packet[12] << 8) | packet[13]),
                operand_3 = ((packet[14] << 24) | (packet[15] << 16) 
                        | (packet[16] << 8) | packet[17]), 
                data = data)
        return message
