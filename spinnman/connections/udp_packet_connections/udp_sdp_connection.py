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
    SpinnmanInvalidPacketException, SpinnmanInvalidParameterException
from spinnman.messages.sdp.sdp_message import SDPMessage
from spinnman.messages.sdp.sdp_header import SDPHeader

import socket
import select


class UDPSDPConnection(AbstractUDPConnection, AbstractSDPReceiver,
                       AbstractSDPSender):

    _SDP_SOURCE_PORT = 7
    _SDP_SOURCE_CPU = 31
    _SDP_SOURCE_CHIP_X = 0
    _SDP_SOURCE_CHIP_Y = 0

    def __init__(self, local_host=None, local_port=None, remote_host=None,
                 remote_port=constants.UDP_CONNECTION_DEFAULT_PORT,
                 default_sdp_tag=0xFF, chip_x=0, chip_y=0):
        AbstractUDPConnection.__init__(self, local_host, local_port,
                                       remote_host, remote_port)

        # Store the default sdp tag
        self._default_sdp_tag = default_sdp_tag

        # Store the chip coordinates
        self._chip_x = chip_x
        self._chip_y = chip_y

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
            if sdp_header.source_port != self._SDP_SOURCE_PORT:
                raise SpinnmanInvalidParameterException(
                    "message.source_port", str(sdp_header.source_port),
                    "The source port must be {} to work with this"
                    " connection".format(self._SDP_SOURCE_PORT))
        else:
            sdp_header.source_port = self._SDP_SOURCE_PORT

        if sdp_header.source_cpu is not None:
            if sdp_header.source_cpu != self._SDP_SOURCE_CPU:
                raise SpinnmanInvalidParameterException(
                    "message.source_cpu", str(sdp_header.source_cpu),
                    "The source cpu must be {} to work with this"
                    " connection".format(self._SDP_SOURCE_CPU))
        else:
            sdp_header.source_cpu = self._SDP_SOURCE_CPU

        if sdp_header.source_chip_x is not None:
            if sdp_header.source_chip_x != self._SDP_SOURCE_CHIP_X:
                raise SpinnmanInvalidParameterException(
                    "message.source_chip_x", str(sdp_header.source_chip_x),
                    "The source chip x must be {} to work with this"
                    " connection".format(self._SDP_SOURCE_CHIP_X))
        else:
            sdp_header.source_chip_x = self._SDP_SOURCE_CHIP_X

        if sdp_header.source_chip_y is not None:
            if sdp_header.source_chip_y != self._SDP_SOURCE_CHIP_Y:
                raise SpinnmanInvalidParameterException(
                    "message.source_chip_y", str(sdp_header.source_chip_y),
                    "The source chip y must be {} to work with this"
                    " connection".format(self._SDP_SOURCE_CHIP_Y))
        else:
            sdp_header.source_chip_y = self._SDP_SOURCE_CHIP_Y

    def connection_label(self):
        return "sdp"