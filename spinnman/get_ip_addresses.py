from spinnman.connections.udp_packet_connections.udp_connection\
    import UDPConnection
from spinnman import constants
import select
from spinnman.exceptions import SpinnmanIOException
import time
import sys
import signal


class GetIpAddressesConnection(UDPConnection):

    def __init__(self, local_host=None,
                 local_port=constants.UDP_BOOT_CONNECTION_DEFAULT_PORT):
        UDPConnection.__init__(self, local_host=local_host,
                                       local_port=local_port)
        self._socket.setblocking(1)

    def connection_type(self):
        return None

    def supports_sends_message(self, message):
        return False

    def receive_ip_address(self, timeout=10.0):
        try:
            self._socket.settimeout(timeout)
            (_, (ip_address, port)) = self._socket.recvfrom(8196)
            if port == 54321:
                return ip_address
            return None
        except Exception:
            return None

if __name__ == "__main__":
    def ctrlc_handler(signal, frame):
        "Exiting"
        sys.exit()

    signal.signal(signal.SIGINT, ctrlc_handler)
    print ("The following addresses might be SpiNNaker boards "
           "(press Ctrl-C to quit):")
    connection = GetIpAddressesConnection()
    while True:
        ip_address = connection.receive_ip_address()
        now = time.time()
        if ip_address is not None:
            print ip_address
