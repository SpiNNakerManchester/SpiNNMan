from abc import ABCMeta
from abc import abstractmethod
from six import add_metaclass

import select
import socket
from spinnman.connections.abstract_classes.abstract_scp_receiver import \
    AbstractSCPReceiver
from spinnman.data.little_endian_byte_array_byte_reader import \
    LittleEndianByteArrayByteReader
from spinnman.exceptions import SpinnmanTimeoutException, SpinnmanIOException, \
    SpinnmanInvalidPacketException


@add_metaclass(ABCMeta)
class AbstractUDPSCPReceiver(AbstractSCPReceiver):
    """ A receiver of SCP messages
    """

    @abstractmethod
    def is_udp_scp_receiver(self):
        pass

    def receive_scp_response(self, scp_response, timeout=None):
        """ Receives an SCP message from this connection.  Blocks\
            until a message has been received, or a timeout occurs.
        
        :param scp_response: The response to fill in
        :rtype scp_response:\
                    :py:class:`spinnman.messages.scp.abstract_scp_response.AbstractSCPResponse`
        :param timeout: The time in seconds to wait for the message to arrive;\
                    if not specified, will wait forever, or until the\
                    connection is closed
        :type timeout: int
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    receiving the message
        :raise spinnman.exceptions.SpinnmanTimeoutException: If there is a\
                    timeout before a message is received
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If the\
                    received packet is not a valid SCP message
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If one\
                    of the fields of the SCP message is invalid
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
