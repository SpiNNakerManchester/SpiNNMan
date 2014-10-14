import socket
from spinnman.connections.abstract_classes.abstract_scp_receiver import \
    AbstractSCPReceiver
from spinnman.connections.abstract_classes.abstract_scp_sender import \
    AbstractSCPSender
from spinnman.connections.abstract_classes.abstract_udp_connection import \
    AbstractUDPConnection
from spinnman import constants
from spinnman.data.little_endian_byte_array_byte_reader import \
    LittleEndianByteArrayByteReader
from spinnman.data.little_endian_byte_array_byte_writer import \
    LittleEndianByteArrayByteWriter
from spinnman.exceptions import SpinnmanIOException, SpinnmanTimeoutException, \
    SpinnmanInvalidPacketException
import select


class UDPSCPConnection(AbstractUDPConnection, AbstractSCPReceiver,
                       AbstractSCPSender):

    def __init__(self, local_host=None, local_port=None, remote_host=None,
                 remote_port=constants.UDP_CONNECTION_DEFAULT_PORT):
        AbstractUDPConnection.__init__(self, local_host, local_port,
                                       remote_host, remote_port)

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