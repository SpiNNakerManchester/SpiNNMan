from spinnman.connections.udp_packet_connections.udp_connection\
    import UDPConnection
from spinnman import constants


class UDPIpAddressesConnection(UDPConnection):
    """ A connection that detects any UDP packet that is transmitted by \
        spinnaker boards prior to boot
    """

    def __init__(self, local_host=None,
                 local_port=constants.UDP_BOOT_CONNECTION_DEFAULT_PORT):
        UDPConnection.__init__(self, local_host=local_host,
                               local_port=local_port)

    def supports_sends_message(self, message):
        return False

    def receive_ip_address(self, timeout=None):
        try:
            (_, (ip_address, port)) = self.receive_with_address(timeout)
            if port == 54321:
                return ip_address
            return None
        except Exception:
            return None

    def __repr__(self):
        return \
            "UDPIpAddressesConnection(local_host={}, local_port={})".format(
                self.local_ip_address, self.local_port)
