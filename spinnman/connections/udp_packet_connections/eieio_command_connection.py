from spinnman.connections.abstract_classes.abstract_callbackable_connection \
    import AbstractCallbackableConnection
from spinnman.connections.abstract_classes.udp_receivers.\
    abstract_udp_eieio_command_receiver import AbstractUDPEIEIOCommandReceiver
from spinnman.connections.abstract_classes.udp_senders.\
    abstract_udp_eieio_command_sender import AbstractUDPEIEIOCommandSender
from spinnman.connections.abstract_classes.abstract_udp_connection\
    import AbstractUDPConnection
from spinnman.connections.listeners.port_listener import PortListener
from spinnman.connections.listeners.queuers.eieio_command_port_queuer import \
    EIEIOCommandPortQueuer
from spinnman.messages.eieio.command_messages.eieio_command_message \
    import EIEIOCommandMessage
from spinnman import constants as spinnman_constants


class EieioCommandConnection(AbstractUDPConnection,
                             AbstractUDPEIEIOCommandReceiver,
                             AbstractUDPEIEIOCommandSender,
                             AbstractCallbackableConnection):

    def __init__(self, listen_port, host_to_notify, port_to_notify):
        AbstractUDPConnection.__init__(
            self, local_port=listen_port, remote_host=host_to_notify,
            remote_port=port_to_notify)
        AbstractCallbackableConnection.__init__(self)

    def is_udp_eieio_command_sender(self):
        return True

    def is_udp_eieio_command_receiver(self):
        return True

    def connection_type(self):
        return None

    def supports_sends_message(self, message):
        return isinstance(message, EIEIOCommandMessage)

    def deregister_callback(self, callback):
        self._callback_listener.deregister_callback(callback)

    def register_callback(
            self, callback,
            traffic_type=spinnman_constants.TRAFFIC_TYPE.EIEIO_COMMAND):
        if self._callback_listener is None:
            eieio_port_queuer = EIEIOCommandPortQueuer(self)
            self._callback_listener = PortListener(callback,
                                                   eieio_port_queuer)
            self._callback_listener.start()

    def close(self):
        if self._callback_listener is not None:
            self._callback_listener.stop()
        AbstractUDPConnection.close(self)
