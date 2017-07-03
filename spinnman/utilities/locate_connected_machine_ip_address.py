"""
locates any spinnaker machines ip address from the auto transmitted packet from
non-booted spinnaker machines
"""

# spinnman imports
from spinnman.connections.udp_packet_connections \
    import IPAddressesConnection

# general imports
import time
import sys
import signal
import socket

# main entrance
if __name__ == "__main__":
    def ctrlc_handler(signal, frame):  # @UnusedVariable
        """

        :param signal:
        :param frame:
        :return: Never returns as it causes a sys.exit()
        """
        "Exiting"
        sys.exit()

    signal.signal(signal.SIGINT, ctrlc_handler)
    print ("The following addresses might be SpiNNaker boards "
           "(press Ctrl-C to quit):")
    connection = IPAddressesConnection()
    seen_boards = set()
    while True:
        ip_address = connection.receive_ip_address()
        now = time.time()
        if ip_address is not None and ip_address not in seen_boards:
            seen_boards.add(ip_address)
            print ip_address, "({})".format(
                socket.gethostbyaddr(ip_address)[0])
