from spinnman.connections.udp_packet_connections.udp_connection\
    import UDPConnection
from spinnman import constants


class UDPIpAddressesConnection(UDPConnection):
    """
    UDPIpAddressesConnection: a connection that detects any UDP packet that
    is trnasmitted by none booted spinnaker boards
    """

    def __init__(self, local_host=None,
                 local_port=constants.UDP_BOOT_CONNECTION_DEFAULT_PORT):
        UDPConnection.__init__(self, local_host=local_host,
                               local_port=local_port)

    def supports_sends_message(self, message):
        """
        overides the udpconnection supports sends messages
        :param message:
        :return:
        """
        return False

    def receive_ip_address(self, timeout=None):
        """

        :param timeout:
        :return:
        """
        try:
            (_, (ip_address, port)) = self.receive_with_address(timeout)
            if port == 54321:
                return ip_address
            return None
        except Exception:
            return None
