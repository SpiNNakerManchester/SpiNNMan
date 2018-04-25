from __future__ import print_function
import time
import sys
import signal
import socket
from spinnman.connections.udp_packet_connections import IPAddressesConnection


def locate_connected_machine(handler):
    """ Locates any SpiNNaker machines IP addresses from the auto-transmitted\
        packets from non-booted SpiNNaker machines.

    :param handler: A callback that decides whether to stop searching. The\
        callback is given two arguments: the IP address found and the current\
        time.
    :type handler: (ipaddr, float) --> bool
    """

    connection = IPAddressesConnection()
    seen_boards = set()
    while True:
        ip_address = connection.receive_ip_address()
        now = time.time()
        if ip_address is not None and ip_address not in seen_boards:
            seen_boards.add(ip_address)
            if handler(ip_address, now):
                break


if __name__ == "__main__":
    def ctrlc_handler(signal, frame):  # @UnusedVariable
        """
        :param signal:
        :param frame:
        :return: Never returns as it causes a sys.exit()
        """
        # pylint: disable=unused-argument
        print("Exiting")
        sys.exit()

    def print_connected(ip_address, timestamp):
        print(ip_address, "({})".format(
            socket.gethostbyaddr(ip_address)[0]), "at", timestamp)
        return False

    print("The following addresses might be SpiNNaker boards "
          "(press Ctrl-C to quit):")
    signal.signal(signal.SIGINT, ctrlc_handler)
    locate_connected_machine(handler=print_connected)
