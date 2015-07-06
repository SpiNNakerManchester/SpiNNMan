from spinnman.connections.udp_packet_connections.udp_connection\
    import UDPConnection
from spinnman import constants
import time
import sys
import signal
import socket


class GetIpAddressesConnection(UDPConnection):

    def __init__(self, local_host=None,
                 local_port=constants.UDP_BOOT_CONNECTION_DEFAULT_PORT):
        UDPConnection.__init__(self, local_host=local_host,
                               local_port=local_port)

    def connection_type(self):
        return None

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

if __name__ == "__main__":
    def ctrlc_handler(signal, frame):
        "Exiting"
        sys.exit()

    signal.signal(signal.SIGINT, ctrlc_handler)
    print ("The following addresses might be SpiNNaker boards "
           "(press Ctrl-C to quit):")
    connection = GetIpAddressesConnection()
    seen_boards = set()
    while True:
        ip_address = connection.receive_ip_address()
        now = time.time()
        if ip_address is not None and ip_address not in seen_boards:
            seen_boards.add(ip_address)
            print ip_address, "({})".format(
                socket.gethostbyaddr(ip_address)[0])
