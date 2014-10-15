from spinnman.connections.abstract_classes.abstract_udp_connection import \
    AbstractUDPConnection
from spinnman import constants
from spinnman.exceptions import SpinnmanIOException


class UDPRawConnection(AbstractUDPConnection):

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
        AbstractUDPConnection.__init__(
            self, local_host, local_port, remote_host, remote_port)

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

    def recieve_raw(self, timeout):
        raise NotImplementedError

    def connection_label(self):
        return "raw"

    def supports_message(self, message):
        if isinstance(message, bytearray):
            return True
        else:
            return False