from .udp_connection import UDPConnection
from spinnman.connections.abstract_classes \
    import EIEIOReceiver, EIEIOSender, Listenable
from spinnman.messages.eieio \
    import read_eieio_command_message, read_eieio_data_message

import struct

_ONE_SHORT = struct.Struct("<H")
_REPR_TEMPLATE = "EIEIOConnection(local_host={}, local_port={},"\
    "remote_host={}, remote_port={})"


class EIEIOConnection(
        UDPConnection, EIEIOReceiver, EIEIOSender, Listenable):
    """ A UDP connection for sending and receiving raw EIEIO messages
    """
    __slots__ = []

    def receive_eieio_message(self, timeout=None):
        data = self.receive(timeout)
        header = _ONE_SHORT.unpack_from(data)[0]
        if header & 0xC000 == 0x4000:
            return read_eieio_command_message(data, 0)
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
