# Copyright (c) 2015 The University of Manchester
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import time
import sys
import signal
import socket
from spinnman.connections.udp_packet_connections import IPAddressesConnection


def locate_connected_machine(handler):
    """
    Locates any SpiNNaker machines IP addresses from the auto-transmitted
    packets from non-booted SpiNNaker machines.

    :param ~collections.abc.Callable handler:
        A callback that decides whether to stop searching. The callback is
        given two arguments: the IP address found and the current time. It
        should return True if the search should cease.
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
    def _ctrlc_handler(sig, frame):  # @UnusedVariable
        """
        :param sig:
        :param frame:
        :return: Never returns as it causes a sys.exit()
        """
        # pylint: disable=unused-argument
        print("Exiting")
        sys.exit()

    def _print_connected(ip_address, timestamp):
        try:
            hostname = f" ({socket.gethostbyaddr(ip_address)[0]})"
        except Exception:  # pylint: disable=broad-except
            hostname = ""
        print(f"{ip_address}{hostname} at {timestamp}")
        return False

    print("The following addresses might be SpiNNaker boards "
          "(press Ctrl-C to quit):")
    signal.signal(signal.SIGINT, _ctrlc_handler)
    locate_connected_machine(handler=_print_connected)
