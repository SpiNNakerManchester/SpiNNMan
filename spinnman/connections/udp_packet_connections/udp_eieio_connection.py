from spinnman.connections.abstract_classes.abstract_eieio_receiver import \
    AbstractEIEIOReceiver
from spinnman.connections.abstract_classes.abstract_eieio_sender import \
    AbstractEIEIOSender
from spinnman.connections.abstract_classes.abstract_udp_connection import \
    AbstractUDPConnection
from spinnman import constants
from spinnman.data.little_endian_byte_array_byte_writer import \
    LittleEndianByteArrayByteWriter
from spinnman.exceptions import SpinnmanIOException


class UDPEIEIOConnection(AbstractUDPConnection, AbstractEIEIOReceiver,
                         AbstractEIEIOSender):

    def __init__(self, local_host=None, local_port=None, remote_host=None,
                 remote_port=constants.UDP_BOOT_CONNECTION_DEFAULT_PORT):
        AbstractUDPConnection.__init__(self, local_host, local_port,
                                       remote_host, remote_port)


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

    def receive_eieio_message(self, timeout=None):
        raise NotImplementedError
