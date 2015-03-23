from spinnman.connections.abstract_classes.udp_receivers\
    .abstract_udp_eieio_command_receiver import AbstractUDPEIEIOCommandReceiver
from spinnman.connections.abstract_classes.udp_receivers.\
    abstract_udp_eieio_data_receiver import AbstractUDPEIEIODataReceiver
from spinnman.connections.abstract_classes.udp_senders\
    .abstract_udp_eieio_command_sender import AbstractUDPEIEIOCommandSender
from spinnman.connections.abstract_classes.udp_senders.\
    abstract_udp_eieio_sender import AbstractUDPEIEIOSender
from spinnman.connections.abstract_classes.abstract_udp_connection import \
    AbstractUDPConnection
from spinnman import constants
from spinnman.exceptions import SpinnmanIOException
from spinnman.messages.eieio.data_messages.eieio_data_message \
    import EIEIODataMessage


class ReverseIPTagConnection(
        AbstractUDPConnection, AbstractUDPEIEIODataReceiver,
        AbstractUDPEIEIOSender, AbstractUDPEIEIOCommandReceiver,
        AbstractUDPEIEIOCommandSender):

    def __init__(self, local_host=None, local_port=None, remote_host=None,
                 remote_port=None):
        AbstractUDPConnection.__init__(self, local_host, local_port,
                                       remote_host, remote_port)
        AbstractUDPEIEIODataReceiver.__init__(self)
        AbstractUDPEIEIOCommandReceiver.__init__(self)
        AbstractUDPEIEIOSender.__init__(self)
        AbstractUDPEIEIOCommandSender.__init__(self)

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

    def receive_raw(self):
        raise NotImplementedError

    def is_eieio_sender(self):
        return True

    def is_udp_eieio_receiver(self):
        return True

    def is_udp_eieio_sender(self):
        return True

    def is_eieio_receiver(self):
        return True

    def is_udp_eieio_command_sender(self):
        return True

    def is_udp_eieio_command_receiver(self):
        return True

    def connection_type(self):
        return constants.CONNECTION_TYPE.REVERSE_IPTAG

    def supports_sends_message(self, message):
        if isinstance(message, bytearray) or isinstance(message,
                                                        EIEIODataMessage):
            return True
        else:
            return False
