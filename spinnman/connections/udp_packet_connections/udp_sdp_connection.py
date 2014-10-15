from spinnman.connections.abstract_classes.abstract_sdp_receiver import \
    AbstractSDPReceiver
from spinnman.connections.abstract_classes.abstract_sdp_sender import \
    AbstractSDPSender
from spinnman.connections.abstract_classes.abstract_udp_connection import \
    AbstractUDPConnection
from spinnman import constants
from spinnman.data.little_endian_byte_array_byte_reader import \
    LittleEndianByteArrayByteReader
from spinnman.data.little_endian_byte_array_byte_writer import \
    LittleEndianByteArrayByteWriter
from spinnman.exceptions import SpinnmanIOException, SpinnmanTimeoutException, \
    SpinnmanInvalidPacketException
from spinnman.messages.sdp.sdp_message import SDPMessage
from spinnman.messages.sdp.sdp_header import SDPHeader
from spinnman.messages.udp_utils.udp_utils import update_sdp_header


import socket
import select


class UDPSDPConnection(AbstractUDPConnection, AbstractSDPReceiver,
                       AbstractSDPSender):

    def __init__(self, local_host=None, local_port=None, remote_host=None,
                 remote_port=None, default_sdp_tag=constants.DEFAULT_SDP_TAG):
        AbstractUDPConnection.__init__(self, local_host, local_port,
                                       remote_host, remote_port)

        # Store the default sdp tag
        self._default_sdp_tag = default_sdp_tag

    def send_sdp_message(self, sdp_message):
        """ See :py:meth:`spinnman.connections.abstract_sdp_sender.AbstractSDPSender.send_sdp_message`

        tag is optional in the message - if not assigned, the default\
        specified in the constructor will be used.
        """
        if not self._can_send:
            raise SpinnmanIOException("Not connected to a remote host")

        # Update the SDP headers for this connection
        update_sdp_header(sdp_message.sdp_header, self._default_sdp_tag)

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

    def connection_label(self):
        return "sdp"

    def supports_message(self, message):
        if isinstance(message, SDPMessage):
            return True
        else:
            return False