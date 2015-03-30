from spinnman import exceptions
from spinnman.connections.abstract_classes.abstract_callbackable_connection\
    import AbstractCallbackableConnection
from spinnman.connections.abstract_classes.abstract_udp_connection\
    import AbstractUDPConnection
from spinnman import constants
from spinnman.connections.abstract_classes.udp_receivers.\
    abstract_udp_eieio_command_receiver import AbstractUDPEIEIOCommandReceiver
from spinnman.connections.abstract_classes.udp_receivers.\
    abstract_udp_eieio_data_receiver import AbstractUDPEIEIODataReceiver
from spinnman.connections.listeners.port_listener import PortListener
from spinnman.connections.listeners.queuers.eieio_command_port_queuer\
    import EIEIOCommandPortQueuer
from spinnman.connections.listeners.queuers.eieio_data_port_queuer\
    import EIEIODataPortQueuer
from spinnman.connections.listeners.queuers.udp_port_queuer\
    import UDPPortQueuer


class StrippedIPTagConnection(
        AbstractUDPConnection, AbstractUDPEIEIODataReceiver,
        AbstractUDPEIEIOCommandReceiver, AbstractCallbackableConnection):

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
        AbstractUDPConnection.__init__(
            self, local_host, local_port, remote_host, remote_port)
        AbstractCallbackableConnection.__init__(self)
        AbstractUDPEIEIOCommandReceiver.__init__(self)
        AbstractUDPEIEIODataReceiver.__init__(self)

    def recieve_raw(self, timeout):
        raise NotImplementedError

    def is_udp_eieio_receiver(self):
        return True

    def connection_type(self):
        return constants.CONNECTION_TYPE.UDP_IPTAG

    def supports_sends_message(self, message):
        return False

    def is_udp_eieio_command_receiver(self):
        return True

    def deregister_callback(self, callback):
        self._callback_listener.deregister_callback(callback)

    def register_callback(self, callback, traffic_type):
        if self._callback_listener is None:
            self._callback_traffic_type = traffic_type
            if traffic_type == constants.TRAFFIC_TYPE.UDP:
                udp_port_queuer = UDPPortQueuer(self)
                self._callback_listener = PortListener(callback,
                                                       udp_port_queuer)
            elif traffic_type == constants.TRAFFIC_TYPE.EIEIO_DATA:
                eieio_port_queuer = EIEIODataPortQueuer(self)
                self._callback_listener = PortListener(callback,
                                                       eieio_port_queuer)
            elif traffic_type == constants.TRAFFIC_TYPE.EIEIO_COMMAND:
                eieio_port_queuer = EIEIOCommandPortQueuer(self)
                self._callback_listener = PortListener(callback,
                                                       eieio_port_queuer)
            else:
                raise exceptions.SpinnmanInvalidParameterException(
                    "traffic_type", traffic_type.name,
                    "The traffic type is not supported by this connection and "
                    "therefore a callback cannot be set for this connection")
            self._callback_listener.start()
        elif self._callback_traffic_type == traffic_type:
            self._callback_listener.register_callback(callback)
        else:
            raise exceptions.SpinnmanInvalidParameterException(
                "traffic_type", traffic_type.name,
                "The traffic type currently supported by this connection for "
                "callbacks is not the same traffic type you have requested"
                "therefore this callback cannot be set for this connection")

    def close(self):
        if self._callback_listener is not None:
            self._callback_listener.stop()
        AbstractUDPConnection.close(self)
