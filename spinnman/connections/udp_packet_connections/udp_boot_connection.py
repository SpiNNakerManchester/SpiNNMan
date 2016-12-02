from spinnman.connections.abstract_classes.abstract_spinnaker_boot_sender \
    import AbstractSpinnakerBootSender
from spinnman.connections.abstract_classes.abstract_spinnaker_boot_receiver \
    import AbstractSpinnakerBootReceiver
from spinnman.connections.udp_packet_connections.udp_connection import \
    UDPConnection
from spinnman.messages.spinnaker_boot.spinnaker_boot_message \
    import SpinnakerBootMessage
from spinnman import constants


class UDPBootConnection(UDPConnection,
                        AbstractSpinnakerBootSender,
                        AbstractSpinnakerBootReceiver):
    """ A connection to the spinnaker board that uses UDP to for booting
    """

    def __init__(self, local_host=None, local_port=None, remote_host=None,
                 remote_port=None):
        """
        :param local_host: The local host name or ip address to bind to.\
                    If not specified defaults to bind to all interfaces,\
                    unless remote_host is specified, in which case binding is\
                    _done to the ip address that will be used to send packets
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

        if remote_port is None:
            remote_port = constants.UDP_BOOT_CONNECTION_DEFAULT_PORT

        UDPConnection.__init__(
            self, local_host, local_port, remote_host, remote_port)
        AbstractSpinnakerBootReceiver.__init__(self)
        AbstractSpinnakerBootSender.__init__(self)

    def send_boot_message(self, boot_message):
        """ See\
            :py:meth:`spinnman.connections.abstract_spinnaker_boot_sender.AbstractSpinnakerBootSender.send_boot_message`
        """
        self.send(boot_message.bytestring)

    def receive_boot_message(self, timeout=None):
        """ See\
            :py:meth:`spinnman.connections.abstract_spinnaker_boot_receiver.AbstractSpinnakerBootReceiver.receive_boot_message`
        """
        data = self.receive(timeout)
        return SpinnakerBootMessage.from_bytestring(data, 0)

    def __repr__(self):
        return\
            "UDPBootConnection(local_host={}, local_port={}, remote_host={},"\
            "remote_port={})".format(
                self.local_ip_address, self.local_port,
                self.remote_ip_address, self.remote_port)
