from .udp_connection import UDPConnection
from spinnman.connections.abstract_classes \
    import EIEIOReceiver, EIEIOSender, Listenable
from spinnman.messages.eieio \
    import read_eieio_command_message, read_eieio_data_message

import struct

_REPR_TEMPLATE = "EIEIOConnection(local_host={}, local_port={},"\
    "remote_host={}, remote_port={})"


class EIEIOConnection(
        UDPConnection, EIEIOReceiver, EIEIOSender,
        Listenable):
    """ A UDP connection for sending and receiving raw EIEIO messages
    """

    def __init__(self, local_host=None, local_port=None, remote_host=None,
                 remote_port=None):
        """

        :param local_host: The optional ip address or host name of the local\
                interface to listen on
        :type local_host: str
        :param local_port: The optional local port to listen on
        :type local_port: int
        :param remote_host: The optional remote host name or ip address to\
                send messages to.  If not specified, sending will not be\
                possible using this connection
        :type remote_host: str
        :param remote_port: The optional remote port number to send messages\
                to.  If not specified, sending will not be possible using this\
                connection
        """
        UDPConnection.__init__(
            self, local_host, local_port, remote_host, remote_port)
        EIEIOReceiver.__init__(self)
        EIEIOSender.__init__(self)
        Listenable.__init__(self)

    def receive_eieio_message(self, timeout=None):
        data = self.receive(timeout)
        header = struct.unpack_from("<H", data)[0]
        if header & 0xC000 == 0x4000:
            return read_eieio_command_message(data, 0)
        else:
            return read_eieio_data_message(data, 0)

    def send_eieio_message(self, eieio_message):
        self.send(eieio_message.bytestring)

    def send_eieio_message_to(self, eieio_message, ip_address, port):
        self.send_to(eieio_message.bytestring, (ip_address, port))

    def get_receive_method(self):
        return self.receive_eieio_message

    def __repr__(self):
        return _REPR_TEMPLATE.format(
            self.local_ip_address, self.local_port,
            self.remote_ip_address, self.remote_port)
