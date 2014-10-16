from abc import ABCMeta
from abc import abstractmethod
from six import add_metaclass

import select
import socket
from spinnman.connections.abstract_classes.abstract_sdp_receiver import \
    AbstractSDPReceiver
from spinnman.data.little_endian_byte_array_byte_reader import \
    LittleEndianByteArrayByteReader
from spinnman.exceptions import SpinnmanTimeoutException, SpinnmanIOException, \
    SpinnmanInvalidPacketException
from spinnman.messages.sdp.sdp_header import SDPHeader
from spinnman.messages.sdp.sdp_message import SDPMessage


@add_metaclass(ABCMeta)
class AbstractUDPSDPReceiver(AbstractSDPReceiver):
    """ A receiver of SDP messages
    """
    @abstractmethod
    def is_udp_sdp_reciever(self):
        pass

    def receive_sdp_message(self, timeout=None):
        """ Receives an SDP message from this connection.  Blocks until the\
            message has been received, or a timeout occurs.
            
        :param timeout: The time in seconds to wait for the message to arrive;\
                    if not specified, will wait forever, or until the\
                    connection is closed
        :type timeout: int
        :return: The received SDP message
        :rtype: :py:class:`spinnman.messages.sdp.sdp_message.SDPMessage`
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    receiving the message
        :raise spinnman.exceptions.SpinnmanTimeoutException: If there is a\
                    timeout before a message is received
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If the\
                    received packet is not a valid SDP message
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If one of\
                    the fields of the SDP message is invalid
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
