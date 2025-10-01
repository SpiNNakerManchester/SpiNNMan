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
import re
from typing import (Dict, Iterable, List, Optional, Tuple)

from spinn_utilities.log import FormatAdapter
from spinn_utilities.typing.coords import XY

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
        extended: bool = False,
        ensure_board_is_ready: bool = True) -> Transceiver:
    """
    Create a Transceiver by creating a :py:class:`~.UDPConnection` to the
    given hostname on port 17893 (the default SCAMP port), and a
    :py:class:`~.BootConnection` on port 54321 (the default boot port),
    optionally discovering any additional links using the UDPConnection,
    and then returning the transceiver created with the conjunction of
    the created UDPConnection and the discovered connections.

    :param hostname: The hostname or IP address of the board or `None` if
        only the BMP connections are of interest
    :param bmp_connection_data:
        the details of the BMP connections used to boot multi-board systems
    :param auto_detect_bmp:
        ``True`` if the BMP of version 4 or 5 boards should be
        automatically determined from the board IP address
    :param power_cycle: If True will power cycle the machine
    :param extended:
        If True will return an Extended version of the Transceiver
    :param ensure_board_is_ready:
        Flag to say if ensure_board_is_ready should be run

    :return: The created transceiver
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
            connections=connections, virtual=True, extended=extended,
            ensure_board_is_ready=ensure_board_is_ready)
    else:
        return create_transceiver_from_connections(
            connections=connections, virtual=False, power_cycle=power_cycle,
            extended=extended, ensure_board_is_ready=ensure_board_is_ready)


def create_transceiver_from_connections(
        connections: Iterable[Connection], virtual: bool = False,
        power_cycle: bool = False, extended: bool = False,
        ensure_board_is_ready: bool = False) -> Transceiver:
    """
    Create a Transceiver with these connections

    :param connections:
        An iterable of connections to the board.  If not specified, no
        communication will be possible until connections are found.
    :param virtual: If True will return a virtual Transceiver
    :param power_cycle: If True will power cycle the machine
    :param extended:
    :param ensure_board_is_ready:
        Flag to say if ensure_board_is_ready should be run
    :return: The created transceiver
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
                connections=connections, power_cycle=power_cycle,
                ensure_board_is_ready=ensure_board_is_ready)
        return Version3Transceiver(
            connections=connections, power_cycle=power_cycle,
            ensure_board_is_ready=ensure_board_is_ready)
    if isinstance(version, Version5):
        if virtual:
            return Virtual5Transceiver(
                connections=connections, power_cycle=power_cycle,
                ensure_board_is_ready=ensure_board_is_ready)
        if extended:
            return ExtendedVersion5Transceiver(
                connections=connections, power_cycle=power_cycle,
                ensure_board_is_ready=ensure_board_is_ready)
        return Version5Transceiver(
            connections=connections, power_cycle=power_cycle,
            ensure_board_is_ready=ensure_board_is_ready)
    raise NotImplementedError(f"No Transceiver for {version=}")


def transceiver_generator(
        bmp_details: Optional[str], auto_detect_bmp: bool,
        scamp_connection_data: Optional[Dict[XY, str]],
        reset_machine_on_start_up: bool,
        ensure_board_is_ready: bool = True) -> Transceiver:
    """
    Makes a transceiver.

    :param bmp_details: the details of the BMP connections
    :param auto_detect_bmp:
        Whether the BMP should be automatically determined
    :param scamp_connection_data:
        Job.connection dict, a String SC&MP connection data or `None`
    :param reset_machine_on_start_up:
        Whether the machine should be reset on startup
    :param ensure_board_is_ready:
        Flag to say if ensure_board_is_ready should be run
    :return: Transceiver, and description of machine it is connected to
    """
    txrx = create_transceiver_from_hostname(
        hostname=SpiNNManDataView.get_ipaddress(),
        bmp_connection_data=_parse_bmp_details(bmp_details),
        auto_detect_bmp=auto_detect_bmp,
        power_cycle=reset_machine_on_start_up,
        ensure_board_is_ready=ensure_board_is_ready)

    # do auto boot if possible
    if scamp_connection_data:
        txrx.add_scamp_connections(scamp_connection_data)
    else:
        txrx.discover_scamp_connections()
    return txrx


def _parse_bmp_cabinet_and_frame(bmp_str: str) -> Tuple[str, Optional[str]]:
    if ";" in bmp_str:
        raise NotImplementedError(
            "cfg bmp_names no longer supports cabinet and frame")
    host = bmp_str.split(",")
    if len(host) == 1:
        return bmp_str, None
    return host[0], host[1]


def _parse_bmp_boards(bmp_boards: str) -> List[int]:
    # If the string is a range of boards, get the range
    range_match = re.match(r"(\d+)-(\d+)", bmp_boards)
    if range_match is not None:
        return list(range(int(range_match.group(1)),
                          int(range_match.group(2)) + 1))

    # Otherwise, assume a list of boards
    return [int(board) for board in bmp_boards.split(",")]


def _parse_bmp_connection(bmp_detail: str) -> BMPConnectionData:
    """
    Parses one item of BMP connection data. Maximal format:
    `cabinet;frame;host,port/boards`

    All parts except host can be omitted. Boards can be a
    hyphen-separated range or a comma-separated list.
    """
    pieces = bmp_detail.split("/")
    (hostname, port_num) = _parse_bmp_cabinet_and_frame(pieces[0])
    # if there is no split, then assume its one board, located at 0
    boards = [0] if len(pieces) == 1 else _parse_bmp_boards(pieces[1])
    port = None if port_num is None else int(port_num)
    return BMPConnectionData(hostname, boards, port)


def _parse_bmp_details(
        bmp_string: Optional[str]) -> Optional[BMPConnectionData]:
    """
    Take a BMP line (a colon-separated list) and split it into the
    BMP connection data.

    :param bmp_string: the BMP string to be converted
    :return: the BMP connection data
    """
    if bmp_string is None or bmp_string == "None":
        return None
    if ":" in bmp_string:
        raise NotImplementedError(
            "bmp_names can no longer contain multiple bmps")
    return _parse_bmp_connection(bmp_string)
