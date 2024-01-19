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
from typing import (List, Optional)
from spinn_utilities.log import FormatAdapter
from spinn_machine.version.version_3 import Version3
from spinn_machine.version.version_5 import Version5
from spinnman.connections.abstract_classes import Connection
from spinnman.data import SpiNNManDataView
from spinnman.extended.version3transceiver import ExtendedVersion3Transceiver
from spinnman.extended.version5transceiver import ExtendedVersion5Transceiver
from spinnman.model.bmp_connection_data import BMPConnectionData
from spinnman.utilities.utility_functions import (
    work_out_bmp_from_machine_details)
from spinnman.connections.udp_packet_connections import (
    BMPConnection, BootConnection, SCAMPConnection)
from spinnman.transceiver import Transceiver
from spinnman.transceiver.version3transceiver import Version3Transceiver
from spinnman.transceiver.version5transceiver import Version5Transceiver
from spinnman.transceiver.virtual5transceiver import Virtual5Transceiver
from spinnman.constants import LOCAL_HOST

logger = FormatAdapter(logging.getLogger(__name__))


def create_transceiver_from_hostname(
        hostname: Optional[str], *,
        bmp_connection_data: Optional[BMPConnectionData] = None,
        auto_detect_bmp: bool = False, power_cycle: bool = False,
        extended: bool = False) -> Transceiver:
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
    :type number_of_boards: int or None
    :param BMPConnectionData bmp_connection_data:
        the details of the BMP connections used to boot multi-board systems
    :param bool auto_detect_bmp:
        ``True`` if the BMP of version 4 or 5 boards should be
        automatically determined from the board IP address
    :param bool power_cycle: If True will power cycle the machine
    :param scamp_connections:
        the list of connections used for SCAMP communications
    :param bool extended:
        If True will return an Extended version of the Transceiver
    :return: The created transceiver
    :rtype: spinnman.transceiver.Transceiver
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
    connections: List[Connection] = list()

    # if no BMP has been supplied, but the board is a spinn4 or a spinn5
    # machine, then an assumption can be made that the BMP is at -1 on the
    # final value of the IP address
    version = SpiNNManDataView.get_machine_version()
    if (isinstance(version, Version5) and auto_detect_bmp is True and
            (bmp_connection_data is None)):
        if hostname is None:
            raise ValueError("hostname is required if deriving BMP details")
        bmp_connection_data = \
            work_out_bmp_from_machine_details(hostname)

    # handle BMP connections
    if bmp_connection_data is not None:
        bmp_connection = BMPConnection(bmp_connection_data)
        connections.append(bmp_connection)
        logger.info("Transceiver using BMP: {}",
                    bmp_connection.remote_ip_address)

    connections.append(SCAMPConnection(remote_host=hostname))

    # handle the boot connection
    connections.append(BootConnection(remote_host=hostname))

    if hostname == LOCAL_HOST:
        return create_transceiver_from_connections(
            connections=connections, virtual=True, extended=extended)
    else:
        return create_transceiver_from_connections(
            connections=connections, virtual=False, power_cycle=power_cycle,
            extended=extended)


def create_transceiver_from_connections(
        connections: List[Connection], virtual: bool = False,
        power_cycle: bool = False, extended: bool = False) -> Transceiver:
    """
    Create a Transceiver with these connections

    :param list(Connection) connections:
        An iterable of connections to the board.  If not specified, no
        communication will be possible until connections are found.
    :param bool virtual: If True will return a virtual Transceiver
    :param bool power_cycle: If True will power cycle the machine
    :param bool extended:
    :return: The created transceiver
    :rtype: spinnman.transceiver.Transceiver
    :raise SpinnmanIOException:
        If there is an error communicating with the board
    :raise SpinnmanInvalidPacketException:
        If a packet is received that is not in the valid format
    :raise SpinnmanInvalidParameterException:
        If a packet is received that has invalid parameters
    :raise SpinnmanUnexpectedResponseCodeException:
        If a response indicates an error during the exchange
    """
    version = SpiNNManDataView.get_machine_version()
    if isinstance(version, Version3):
        if virtual:
            raise NotImplementedError(f"No Virtual Transceiver for {version=}")
        if extended:
            return ExtendedVersion3Transceiver(
                connections=connections, power_cycle=power_cycle)
        return Version3Transceiver(
            connections=connections, power_cycle=power_cycle)
    if isinstance(version, Version5):
        if virtual:
            return Virtual5Transceiver(
                connections=connections, power_cycle=power_cycle)
        if extended:
            return ExtendedVersion5Transceiver(
                connections=connections, power_cycle=power_cycle)
        return Version5Transceiver(
            connections=connections, power_cycle=power_cycle)
    raise NotImplementedError(f"No Transceiver for {version=}")
