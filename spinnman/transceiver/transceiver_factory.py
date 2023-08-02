# Copyright (c) 2023 The University of Manchester
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

import logging
from spinn_utilities.log import FormatAdapter
from spinnman.utilities.utility_functions import (
    work_out_bmp_from_machine_details)
from spinnman.connections.udp_packet_connections import (
    BMPConnection, BootConnection, SCAMPConnection)
from spinnman.transceiver.base_transceiver import BaseTransceiver

logger = FormatAdapter(logging.getLogger(__name__))


def create_transceiver_from_hostname(
        hostname, version, bmp_connection_data=None, number_of_boards=None,
        auto_detect_bmp=False):
    """
    Create a Transceiver by creating a :py:class:`~.UDPConnection` to the
    given hostname on port 17893 (the default SCAMP port), and a
    :py:class:`~.BootConnection` on port 54321 (the default boot port),
    optionally discovering any additional links using the UDPConnection,
    and then returning the transceiver created with the conjunction of
    the created UDPConnection and the discovered connections.

    :param hostname: The hostname or IP address of the board or `None` if
        only the BMP connections are of interest
    :type hostname: str or None
    :param number_of_boards: a number of boards expected to be supported, or
        ``None``, which defaults to a single board
    :type number_of_boards: int or None
    :param int version: the type of SpiNNaker board used within the SpiNNaker
        machine being used. If a Spinn-5 board, then the version will be 5,
        Spinn-3 would equal 3 and so on.
    :param list(BMPConnectionData) bmp_connection_data:
        the details of the BMP connections used to boot multi-board systems
    :param bool auto_detect_bmp:
        ``True`` if the BMP of version 4 or 5 boards should be
        automatically determined from the board IP address
    :param scamp_connections:
        the list of connections used for SCAMP communications
    :return: The created transceiver
    :rtype: Transceiver
    :raise SpinnmanIOException:
        If there is an error communicating with the board
    :raise SpinnmanInvalidPacketException:
        If a packet is received that is not in the valid format
    :raise SpinnmanInvalidParameterException:
        If a packet is received that has invalid parameters
    :raise SpinnmanUnexpectedResponseCodeException:
        If a response indicates an error during the exchange
    """
    if hostname is not None:
        logger.info("Creating transceiver for {}", hostname)
    connections = list()

    # if no BMP has been supplied, but the board is a spinn4 or a spinn5
    # machine, then an assumption can be made that the BMP is at -1 on the
    # final value of the IP address
    if (version >= 4 and auto_detect_bmp is True and
            (bmp_connection_data is None or not bmp_connection_data)):
        bmp_connection_data = [
            work_out_bmp_from_machine_details(hostname, number_of_boards)]

    # handle BMP connections
    if bmp_connection_data is not None:
        bmp_ip_list = list()
        for conn_data in bmp_connection_data:
            bmp_connection = BMPConnection(conn_data)
            connections.append(bmp_connection)
            bmp_ip_list.append(bmp_connection.remote_ip_address)
        logger.info("Transceiver using BMPs: {}", bmp_ip_list)

    connections.append(SCAMPConnection(remote_host=hostname))

    # handle the boot connection
    connections.append(BootConnection(remote_host=hostname))

    return BaseTransceiver(version, connections=connections)
