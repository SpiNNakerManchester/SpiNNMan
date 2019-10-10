# Copyright (c) 2017-2019 The University of Manchester
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
    def ctrlc_handler(sig, frame):  # @UnusedVariable
        """
        :param sig:
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
