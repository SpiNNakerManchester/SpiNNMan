from spinn_utilities.overrides import overrides
from spinnman.connections.abstract_classes import Listenable
from spinnman.connections.udp_packet_connections import UDPConnection


class UDPListenableConnection(UDPConnection, Listenable):

    def __init__(self, local_host=None, local_port=None, remote_host=None,
                 remote_port=None):
        UDPConnection.__init__(
            self, local_host=local_host, local_port=local_port,
            remote_host=remote_host, remote_port=remote_port)
        Listenable.__init__(self)

    @overrides(Listenable.get_receive_method)
    def get_receive_method(self):
        return self.receive
