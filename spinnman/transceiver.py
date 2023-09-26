# Copyright (c) 2014 The University of Manchester
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

# pylint: disable=too-many-arguments
import io
import os
import random
import struct
from threading import Condition
from collections import defaultdict
from contextlib import contextmanager, suppress
import logging
import socket
import time
from spinn_utilities.config_holder import get_config_bool
from spinn_utilities.abstract_context_manager import AbstractContextManager
from spinn_utilities.log import FormatAdapter
from spinn_machine import CoreSubsets
from spinnman.constants import (
    BMP_POST_POWER_ON_SLEEP_TIME, BMP_POWER_ON_TIMEOUT, BMP_TIMEOUT,
    CPU_MAX_USER, CPU_USER_OFFSET, CPU_USER_START_ADDRESS,
    IPTAG_TIME_OUT_WAIT_TIMES, SCP_SCAMP_PORT, SYSTEM_VARIABLE_BASE_ADDRESS,
    UDP_BOOT_CONNECTION_DEFAULT_PORT, NO_ROUTER_DIAGNOSTIC_FILTERS,
    ROUTER_REGISTER_BASE_ADDRESS, ROUTER_DEFAULT_FILTERS_MAX_POSITION,
    ROUTER_FILTER_CONTROLS_OFFSET, ROUTER_DIAGNOSTIC_FILTER_SIZE, N_RETRIES,
    BOOT_RETRIES)
from spinnman.data import SpiNNManDataView
from spinnman.exceptions import (
    SpinnmanInvalidParameterException, SpinnmanException, SpinnmanIOException,
    SpinnmanTimeoutException, SpinnmanGenericProcessException,
    SpinnmanUnexpectedResponseCodeException,
    SpiNNManCoresNotInStateException)
from spinnman.model import MachineDimensions
from spinnman.model.enums import (
    CPUState, SDP_PORTS, SDP_RUNNING_MESSAGE_CODES)
from spinnman.messages.scp.impl.get_chip_info import GetChipInfo
from spinnman.messages.sdp import SDPFlag, SDPHeader, SDPMessage
from spinnman.messages.spinnaker_boot import (
    SystemVariableDefinition, SpinnakerBootMessages)
from spinnman.messages.scp.enums import PowerCommand
from spinnman.messages.scp.abstract_messages import AbstractSCPRequest
from spinnman.messages.scp.impl import (
    BMPGetVersion, SetPower, ReadFPGARegister,
    WriteFPGARegister, IPTagSetTTO, ReverseIPTagSet,
    CountState, WriteMemory, SendSignal, AppStop,
    IPTagSet, IPTagClear, RouterClear, DoSync)
from spinnman.connections.udp_packet_connections import (
    BMPConnection, BootConnection, SCAMPConnection)
from spinnman.processes import (
    GetMachineProcess, GetVersionProcess,
    MallocSDRAMProcess, WriteMemoryProcess, ReadMemoryProcess,
    GetCPUInfoProcess, GetExcludeCPUInfoProcess, GetIncludeCPUInfoProcess,
    ReadIOBufProcess, ApplicationRunProcess,
    LoadFixedRouteRoutingEntryProcess, FixedConnectionSelector,
    ReadFixedRouteRoutingEntryProcess,
    LoadMultiCastRoutesProcess, GetTagsProcess, GetMultiCastRoutesProcess,
    SendSingleCommandProcess, ReadRouterDiagnosticsProcess,
    MostDirectConnectionSelector, ApplicationCopyRunProcess)
from spinnman.utilities.utility_functions import (
    get_vcpu_address, work_out_bmp_from_machine_details)

logger = FormatAdapter(logging.getLogger(__name__))

_SCAMP_NAME = "SC&MP"
_SCAMP_VERSION = (3, 0, 1)

_BMP_NAME = "BC&MP"
_BMP_MAJOR_VERSIONS = [1, 2]

_CONNECTION_CHECK_RETRIES = 3
INITIAL_FIND_SCAMP_RETRIES_COUNT = 3

_ONE_BYTE = struct.Struct("B")
_TWO_BYTES = struct.Struct("<BB")
_FOUR_BYTES = struct.Struct("<BBBB")
_ONE_WORD = struct.Struct("<I")
_ONE_LONG = struct.Struct("<Q")
_EXECUTABLE_ADDRESS = 0x67800000


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
    :param BMPConnectionData bmp_connection_data:
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
        bmp_connection = BMPConnection(bmp_connection_data)
        connections.append(bmp_connection)
        logger.info("Transceiver using BMP: {}",
                    bmp_connection.remote_ip_address)

    connections.append(SCAMPConnection(remote_host=hostname))

    # handle the boot connection
    connections.append(BootConnection(remote_host=hostname))

    return Transceiver(version, connections=connections)


class Transceiver(AbstractContextManager):
    """
    An encapsulation of various communications with the SpiNNaker board.

    The methods of this class are designed to be thread-safe (provided they do
    not access a BMP, as access to those is never thread-safe);
    thus you can make multiple calls to the same (or different) methods
    from multiple threads and expect each call to work as if it had been
    called sequentially, although the order of returns is not guaranteed.

    .. note::
        With multiple connections to the board, using multiple threads in this
        way may result in an increase in the overall speed of operation, since
        the multiple calls may be made separately over the set of given
        connections.
    """
    __slots__ = [
        "_all_connections",
        "_bmp_selector",
        "_bmp_connection",
        "_boot_send_connection",
        "_chip_execute_lock_condition",
        "_chip_execute_locks",
        "_height",
        "_iobuf_size",
        "_machine_off",
        "_n_chip_execute_locks",
        "_scamp_connection_selector",
        "_scamp_connections",
        "_udp_scamp_connections",
        "_version",
        "_width"]

    def __init__(
            self, version, connections=None):
        """
        :param int version: The version of the board being connected to
        :param list(Connection) connections:
            An iterable of connections to the board.  If not specified, no
            communication will be possible until connections are found.
        :raise SpinnmanIOException:
            If there is an error communicating with the board, or if no
            connections to the board can be found (if connections is ``None``)
        :raise SpinnmanInvalidPacketException:
            If a packet is received that is not in the valid format
        :raise SpinnmanInvalidParameterException:
            If a packet is received that has invalid parameters
        :raise SpinnmanUnexpectedResponseCodeException:
            If a response indicates an error during the exchange
        """
        # Place to keep the current machine
        self._version = version
        self._width = None
        self._height = None
        self._iobuf_size = None

        # A set of the original connections - used to determine what can
        # be closed
        if connections is None:
            connections = list()

        # A set of all connection - used for closing
        self._all_connections = set()
        self._all_connections.update(connections)

        # A boot send connection - there can only be one in the current system,
        # or otherwise bad things can happen!
        self._boot_send_connection = None

        # A dict of IP address -> SCAMP connection
        # These are those that can be used for setting up IP Tags
        self._udp_scamp_connections = dict()

        # A list of all connections that can be used to send and receive SCP
        # messages for SCAMP interaction
        self._scamp_connections = list()

        # The BMP connections
        self._bmp_connection = None

        # build connection selectors for the processes.
        self._bmp_selector = None
        self._scamp_connection_selector = \
            self.__identify_connections(connections)

        # A lock against single chip executions (entry is (x, y))
        # The condition should be acquired before the locks are
        # checked or updated
        # The write lock condition should also be acquired to avoid a flood
        # fill during an individual chip execute
        self._chip_execute_locks = defaultdict(Condition)
        self._chip_execute_lock_condition = Condition()
        self._n_chip_execute_locks = 0

        # Check that the BMP connections are valid
        self.__check_bmp_connection()

        self._machine_off = False

    def _where_is_xy(self, x, y):
        """
        Attempts to get where_is_x_y info from the machine

        If no machine will do its best.

        :param int x:
        :param int y:
        :rtype: str
        """
        try:
            if SpiNNManDataView.has_machine():
                return SpiNNManDataView.get_machine().where_is_xy(x, y)
            return (f"No Machine. "
                    f"Root IP:{self._scamp_connections[0].remote_ip_address}"
                    f"x:{x} y:{y}")
        except Exception as ex:  # pylint: disable=broad-except
            return str(ex)

    def __identify_connections(self, connections):
        for conn in connections:

            # locate the only boot send conn
            if isinstance(conn, BootConnection):
                if self._boot_send_connection is not None:
                    raise SpinnmanInvalidParameterException(
                        "connections", f"[... {conn} ...]",
                        "Only a single SpinnakerBootSender can be specified")
                self._boot_send_connection = conn

            # Locate any connections that talk to a BMP
            if isinstance(conn, BMPConnection):
                # If it is a BMP conn, add it here
                if self._bmp_connection is not None:
                    raise NotImplementedError(
                        "Only one BMP connection supported")
                self._bmp_connection = conn
                self._bmp_selector = FixedConnectionSelector(conn)
            # Otherwise, check if it can send and receive SCP (talk to SCAMP)
            elif isinstance(conn, SCAMPConnection):
                self._scamp_connections.append(conn)

        # update the transceiver with the conn selectors.
        return MostDirectConnectionSelector(self._scamp_connections)

    def __check_bmp_connection(self):
        """
        Check that the BMP connections are actually connected to valid BMPs.

        :raise SpinnmanIOException: when a connection is not linked to a BMP
        """
        # check that the UDP BMP conn is actually connected to a BMP
        # via the sver command
        if self._bmp_connection is not None:
            conn = self._bmp_connection

            # try to send a BMP sver to check if it responds as expected
            try:
                version_info = self._get_scamp_version(
                    conn.chip_x, conn.chip_y, self._bmp_selector)
                fail_version_name = version_info.name != _BMP_NAME
                fail_version_num = \
                    version_info.version_number[0] not in _BMP_MAJOR_VERSIONS
                if fail_version_name or fail_version_num:
                    raise SpinnmanIOException(
                        f"The BMP at {conn.remote_ip_address} is running "
                        f"{version_info.name} {version_info.version_string} "
                        "which is incompatible with this transceiver, required"
                        f" version is {_BMP_NAME} {_BMP_MAJOR_VERSIONS}")

                logger.info("Using BMP at {} with version {} {}",
                            conn.remote_ip_address, version_info.name,
                            version_info.version_string)

            # If it fails to respond due to timeout, maybe that the connection
            # isn't valid
            except SpinnmanTimeoutException as e:
                raise SpinnmanException(
                    f"BMP connection to {conn.remote_ip_address} is "
                    "not responding") from e
            except Exception:
                logger.exception("Failed to speak to BMP at {}",
                                 conn.remote_ip_address)
                raise

    def _check_connection(
            self, connection_selector, chip_x, chip_y):
        """
        Check that the given connection to the given chip works.

        :param connection_selector: the connection selector to use
        :type connection_selector:
            AbstractMultiConnectionProcessConnectionSelector
        :param int chip_x: the chip x coordinate to try to talk to
        :param int chip_y: the chip y coordinate to try to talk to
        :return: True if a valid response is received, False otherwise
        :rtype: ChipInfo or None
        """
        for _ in range(_CONNECTION_CHECK_RETRIES):
            try:
                sender = SendSingleCommandProcess(connection_selector)
                chip_info = sender.execute(  # pylint: disable=no-member
                    GetChipInfo(chip_x, chip_y)).chip_info
                if not chip_info.is_ethernet_available:
                    time.sleep(0.1)
                else:
                    return chip_info
            except (SpinnmanGenericProcessException, SpinnmanTimeoutException,
                    SpinnmanUnexpectedResponseCodeException):
                pass
            except SpinnmanIOException:
                break
        return None

    @contextmanager
    def __flood_execute_lock(self):
        """
        Get a lock for executing a flood fill of an executable.
        """
        # Get the execute lock all together, so nothing can access it
        with self._chip_execute_lock_condition:
            # Wait until nothing is executing
            self._chip_execute_lock_condition.wait_for(
                lambda: self._n_chip_execute_locks < 1)
            yield self._chip_execute_lock_condition

    @staticmethod
    def _get_random_connection(connections):
        """
        Returns the given connection, or else picks one at random.

        :param list(Connection) connections:
            the list of connections to locate a random one from
        :return: a connection object
        :rtype: Connection or None
        """
        if not connections:
            return None
        return connections[random.randint(0, len(connections) - 1)]

    def send_sdp_message(self, message, connection=None):
        """
        Sends an SDP message using one of the connections.

        :param SDPMessage message: The message to send
        :param SDPConnection connection: An optional connection to use
        """
        if connection is None:
            connection_to_use = self._get_random_connection(
                self._scamp_connections)
        else:
            connection_to_use = connection
        connection_to_use.send_sdp_message(message)

    def _check_and_add_scamp_connections(self, x, y, ip_address):
        """
        :param int x: X coordinate of target chip
        :param int y: Y coordinate of target chip
        :param str ip_address: IP address of target chip

        :raise SpinnmanIOException:
            If there is an error communicating with the board
        :raise SpinnmanInvalidPacketException:
            If a packet is received that is not in the valid format
        :raise SpinnmanInvalidParameterException:
            If a packet is received that has invalid parameters
        :raise SpinnmanUnexpectedResponseCodeException:
            If a response indicates an error during the exchange
        """
        conn = SCAMPConnection(remote_host=ip_address, chip_x=x, chip_y=y)

        # check if it works
        chip_info = self._check_connection(FixedConnectionSelector(conn), x, y)
        if chip_info is not None:
            self._all_connections.add(conn)
            self._udp_scamp_connections[chip_info.ethernet_ip_address] = conn
            self._scamp_connections.append(conn)
        else:
            logger.warning(
                "Additional Ethernet connection on {} at chip {}, {} "
                "cannot be contacted", ip_address, x, y)

    def discover_scamp_connections(self):
        """
        Find connections to the board and store these for future use.

        .. note::
            An exception will be thrown if no initial connections can be
            found to the board.

        :raise SpinnmanIOException:
            If there is an error communicating with the board
        :raise SpinnmanInvalidPacketException:
            If a packet is received that is not in the valid format
        :raise SpinnmanInvalidParameterException:
            If a packet is received that has invalid parameters
        :raise SpinnmanUnexpectedResponseCodeException:
            If a response indicates an error during the exchange
        """
        # Currently, this only finds other UDP connections given a connection
        # that supports SCP - this is done via the machine
        if not self._scamp_connections:
            return list()

        # Get the machine dimensions
        dims = self._get_machine_dimensions()

        # Find all the new connections via the machine Ethernet-connected chips
        version = SpiNNManDataView.get_machine_version()
        for x, y in version.get_potential_ethernet_chips(
                dims.width, dims.height):
            ip_addr_item = SystemVariableDefinition.ethernet_ip_address
            try:
                # TODO avoid here_is_x,y if read_memory fails
                data = self.read_memory(
                    x, y,
                    SYSTEM_VARIABLE_BASE_ADDRESS + ip_addr_item.offset, 4)
            except SpinnmanGenericProcessException:
                continue
            ip = _FOUR_BYTES.unpack_from(data)
            ip_address = f"{ip[0]}.{ip[1]}.{ip[2]}.{ip[3]}"
            logger.info(ip_address)
            self._check_and_add_scamp_connections(x, y, ip_address)
        self._scamp_connection_selector = MostDirectConnectionSelector(
            self._scamp_connections)

    def add_scamp_connections(self, connections):
        """
        Check connections to the board and store these for future use.

        .. note::
            An exception will be thrown if no initial connections can be
            found to the board.

        :param dict((int,int),str) connections:
            Dict of (`x`,`y`) to IP address
        :raise SpinnmanIOException:
            If there is an error communicating with the board
        :raise SpinnmanInvalidPacketException:
            If a packet is received that is not in the valid format
        :raise SpinnmanInvalidParameterException:
            If a packet is received that has invalid parameters
        :raise SpinnmanUnexpectedResponseCodeException:
            If a response indicates an error during the exchange
        """
        for ((x, y), ip_address) in connections.items():
            self._check_and_add_scamp_connections(x, y, ip_address)
        self._scamp_connection_selector = MostDirectConnectionSelector(
            self._scamp_connections)

    def _get_machine_dimensions(self):
        """
        Get the maximum chip X-coordinate and maximum chip Y-coordinate of
        the chips in the machine.

        :return: The dimensions of the machine
        :rtype: MachineDimensions
        :raise SpinnmanIOException:
            If there is an error communicating with the board
        :raise SpinnmanInvalidPacketException:
            If a packet is received that is not in the valid format
        :raise SpinnmanInvalidParameterException:
            If a packet is received that has invalid parameters
        :raise SpinnmanUnexpectedResponseCodeException:
            If a response indicates an error during the exchange
        """
        if self._width is None or self._height is None:
            height_item = SystemVariableDefinition.y_size
            self._height, self._width = _TWO_BYTES.unpack_from(
                self.read_memory(
                    AbstractSCPRequest.DEFAULT_DEST_X_COORD,
                    AbstractSCPRequest.DEFAULT_DEST_Y_COORD,
                    SYSTEM_VARIABLE_BASE_ADDRESS + height_item.offset,
                    2))
        return MachineDimensions(self._width, self._height)

    def get_machine_details(self):
        """
        Get the details of the machine made up of chips on a board and how
        they are connected to each other.

        :return: A machine description
        :rtype: ~spinn_machine.Machine
        :raise SpinnmanIOException:
            If there is an error communicating with the board
        :raise SpinnmanInvalidPacketException:
            If a packet is received that is not in the valid format
        :raise SpinnmanInvalidParameterException:
            If a packet is received that has invalid parameters
        :raise SpinnmanUnexpectedResponseCodeException:
            If a response indicates an error during the exchange
        """
        # Get the width and height of the machine
        self._get_machine_dimensions()

        # Get the coordinates of the boot chip
        version_info = self._get_scamp_version()

        # Get the details of all the chips
        get_machine_process = GetMachineProcess(
            self._scamp_connection_selector)
        machine = get_machine_process.get_machine_details(
            version_info.x, version_info.y, self._width, self._height)

        # Work out and add the SpiNNaker links and FPGA links
        machine.add_spinnaker_links()
        machine.add_fpga_links()

        if self._boot_send_connection:
            logger.info(f"Detected {machine.summary_string()}")
        return machine

    def _get_scamp_version(
            self, chip_x=AbstractSCPRequest.DEFAULT_DEST_X_COORD,
            chip_y=AbstractSCPRequest.DEFAULT_DEST_Y_COORD,
            connection_selector=None, n_retries=N_RETRIES):
        """
        Get the version of SCAMP which is running on the board.

        :param int chip_x: the chip's x coordinate to query for SCAMP version
        :param int chip_y: the chip's y coordinate to query for SCAMP version
        :param connection_selector: the connection to send the SCAMP
            version or `None` (if `None` then a random SCAMP connection is
            used).
        :type connection_selector:
            AbstractMultiConnectionProcessConnectionSelector
        :param int n_retries:
        :return: The version identifier
        :rtype: VersionInfo
        :raise SpinnmanIOException:
            If there is an error communicating with the board
        :raise SpinnmanInvalidParameterException:
            If the timeout is less than 1
        :raise SpinnmanTimeoutException:
            If none of the retries resulted in a response before the timeout
            (suggesting that the board is not booted).
        """
        if connection_selector is None:
            connection_selector = self._scamp_connection_selector
        process = GetVersionProcess(connection_selector, n_retries)
        return process.get_version(x=chip_x, y=chip_y, p=0)

    def _boot_board(self, extra_boot_values=None):
        """
        Attempt to boot the board. No check is performed to see if the
        board is already booted.

        :param dict(SystemVariableDefinition,object) extra_boot_values:
            extra values to set during boot
            Any additional or overwrite values to set during boot.
            This should only be used for values which are not standard
            based on the board version.
        :raise SpinnmanInvalidParameterException:
            If the board version is not known
        :raise SpinnmanIOException:
            If there is an error communicating with the board
        """
        if not self._boot_send_connection:
            # No can do. Can't boot without a boot connection.
            raise SpinnmanIOException("no boot connection available")
        boot_messages = SpinnakerBootMessages(
            board_version=self._version, extra_boot_values=extra_boot_values)
        for boot_message in boot_messages.messages:
            self._boot_send_connection.send_boot_message(boot_message)
        time.sleep(2.0)

    @staticmethod
    def _is_scamp_version_compabible(version):
        """
        Determine if the version of SCAMP is compatible with this transceiver.

        :param tuple(int,int,int) version: The version to test
        :rtype: bool
        """

        # The major version must match exactly
        if version[0] != _SCAMP_VERSION[0]:
            return False

        # If the minor version matches, the patch version must be >= the
        # required version
        if version[1] == _SCAMP_VERSION[1]:
            return version[2] >= _SCAMP_VERSION[2]

        # If the minor version is > than the required version, the patch
        # version is irrelevant
        return version[1] > _SCAMP_VERSION[1]

    def ensure_board_is_ready(self, n_retries=5, extra_boot_values=None):
        """
        Ensure that the board is ready to interact with this version of the
        transceiver. Boots the board if not already booted and verifies that
        the version of SCAMP running is compatible with this transceiver.

        :param int n_retries: The number of times to retry booting
        :param dict(SystemVariableDefinition,object) extra_boot_values:
            Any additional or overwrite values to set during boot.
            This should only be used for values which are not standard
            based on the board version.
        :return: The version identifier
        :rtype: VersionInfo
        :raise SpinnmanIOException:
            * If there is a problem booting the board
            * If the version of software on the board is not compatible with
              this transceiver
        """
        # try to get a SCAMP version once
        logger.info("Working out if machine is booted")
        if self._machine_off:
            version_info = None
        else:
            version_info = self._try_to_find_scamp_and_boot(
                INITIAL_FIND_SCAMP_RETRIES_COUNT, extra_boot_values)

        # If we fail to get a SCAMP version this time, try other things
        if version_info is None and self._bmp_connection is not None:

            # start by powering up each BMP connection
            logger.info("Attempting to power on machine")
            self._power_on_machine()

            # Sleep a bit to let things get going
            time.sleep(2.0)
            logger.info("Attempting to boot machine")

            # retry to get a SCAMP version, this time trying multiple times
            version_info = self._try_to_find_scamp_and_boot(
                n_retries, extra_boot_values)

        # verify that the version is the expected one for this transceiver
        if version_info is None:
            raise SpinnmanIOException(
                "Failed to communicate with the machine")
        if (version_info.name != _SCAMP_NAME or
                not self._is_scamp_version_compabible(
                    version_info.version_number)):
            raise SpinnmanIOException(
                f"The machine is currently booted with {version_info.name}"
                f" {version_info.version_number} which is incompatible with "
                "this transceiver, required version is "
                f"{_SCAMP_NAME} {_SCAMP_VERSION}")

        logger.info("Machine communication successful")

        # Change the default SCP timeout on the machine, keeping the old one to
        # revert at close
        for scamp_connection in self._scamp_connections:
            process = SendSingleCommandProcess(self._scamp_connection_selector)
            process.execute(IPTagSetTTO(
                scamp_connection.chip_x, scamp_connection.chip_y,
                IPTAG_TIME_OUT_WAIT_TIMES.TIMEOUT_2560_ms))

            chip_info = self._check_connection(
                FixedConnectionSelector(scamp_connection),
                scamp_connection.chip_x, scamp_connection.chip_y)
            if chip_info is not None:
                self._udp_scamp_connections[chip_info.ethernet_ip_address] = \
                    scamp_connection

        # Update the connection selector so that it can ask for processor ids
        self._scamp_connection_selector = MostDirectConnectionSelector(
            self._scamp_connections)

        return version_info

    def __is_default_destination(self, version_info):
        return (version_info.x == AbstractSCPRequest.DEFAULT_DEST_X_COORD
                and version_info.y == AbstractSCPRequest.DEFAULT_DEST_Y_COORD)

    def _try_to_find_scamp_and_boot(self, tries_to_go, extra_boot_values):
        """
        Try to detect if SCAMP is running, and if not, boot the machine.

        :param int tries_to_go: how many attempts should be supported
        :param dict(SystemVariableDefinition,object) extra_boot_values:
            Any additional or overwrite values to set during boot.
            This should only be used for values which are not standard
            based on the board version.
        :return: version info
        :rtype: VersionInfo
        :raise SpinnmanIOException:
            If there is a problem communicating with the machine
        """
        version_info = None
        current_tries_to_go = tries_to_go
        while version_info is None and current_tries_to_go > 0:
            try:
                version_info = self._get_scamp_version(n_retries=BOOT_RETRIES)
                if self.__is_default_destination(version_info):
                    version_info = None
                    time.sleep(0.1)
            except SpinnmanGenericProcessException as e:
                if isinstance(e.exception, SpinnmanTimeoutException):
                    logger.info("Attempting to boot machine")
                    self._boot_board(extra_boot_values)
                    current_tries_to_go -= 1
                elif isinstance(e.exception, SpinnmanIOException):
                    raise SpinnmanIOException(
                        "Failed to communicate with the machine") from e
                else:
                    raise
            except SpinnmanTimeoutException:
                logger.info("Attempting to boot machine")
                self._boot_board(extra_boot_values)
                current_tries_to_go -= 1
            except SpinnmanIOException as e:
                raise SpinnmanIOException(
                    "Failed to communicate with the machine") from e

        # The last thing we tried was booting, so try again to get the version
        if version_info is None:
            with suppress(SpinnmanException):
                version_info = self._get_scamp_version()
                if self.__is_default_destination(version_info):
                    version_info = None
        if version_info is not None:
            logger.info("Found board with version {}", version_info)
        return version_info

    def get_cpu_infos(
            self, core_subsets=None, states=None, include=True):
        """
        Get information about the processors on the board.

        :param ~spinn_machine.CoreSubsets core_subsets:
            A set of chips and cores from which to get the
            information. If not specified, the information from all of the
            cores on all of the chips on the board are obtained.
        :param states: The state or states to filter on (if any)
        :type states: None, CPUState or collection(CPUState)
        :param bool include:
            If True includes only infos in the requested state(s).
            If False includes only infos NOT in the requested state(s).
            Ignored if states is None.
        :return: The CPU information for the selected cores and States, or
            all cores/states  if core_subsets/states is not specified
        :rtype: ~spinnman.model.CPUInfos
        :raise SpinnmanIOException:
            If there is an error communicating with the board
        :raise SpinnmanInvalidPacketException:
            If a packet is received that is not in the valid format
        :raise SpinnmanInvalidParameterException:
            * If chip_and_cores contains invalid items
            * If a packet is received that has invalid parameters
        :raise SpinnmanUnexpectedResponseCodeException:
            If a response indicates an error during the exchange
        """
        # Get all the cores if the subsets are not given
        if core_subsets is None:
            core_subsets = CoreSubsets()
            for chip in SpiNNManDataView.get_machine().chips:
                for processor in chip.processors:
                    core_subsets.add_processor(
                        chip.x, chip.y, processor.processor_id)

        if states is None:
            process = GetCPUInfoProcess(self._scamp_connection_selector)
        else:
            if isinstance(states, CPUState):
                new_states = set()
                new_states.add(states)
                states = new_states
            if include:
                process = GetIncludeCPUInfoProcess(
                    self._scamp_connection_selector, states)
            else:
                process = GetExcludeCPUInfoProcess(
                    self._scamp_connection_selector, states)

        cpu_info = process.get_cpu_info(core_subsets)
        return cpu_info

    def get_clock_drift(self, x, y):
        """
        Get the clock drift
        :param int x: The x-coordinate of the chip to get drift for
        :param int y: The y-coordinate of the chip to get drift for
        """
        DRIFT_FP = 1 << 17

        drift = self._get_sv_data(x, y, SystemVariableDefinition.clock_drift)
        drift = struct.unpack("<i", struct.pack("<I", drift))[0]
        drift = drift / DRIFT_FP
        return drift

    def _get_sv_data(self, x, y, data_item):
        """
        :param int x:
        :param int y:
        :param SystemVariableDefinition data_item:
        """
        addr = SYSTEM_VARIABLE_BASE_ADDRESS + data_item.offset
        if data_item.data_type.is_byte_array:
            # Do not need to decode the bytes of a byte array
            return self.read_memory(x, y, addr, data_item.array_size)
        return struct.unpack_from(
            data_item.data_type.struct_code,
            self.read_memory(x, y, addr, data_item.data_type.value))[0]

    @staticmethod
    def __get_user_register_address_from_core(p, user):
        """
        Get the address of user 0 for a given processor on the board.

        .. note::
            Conventionally, user_0 usually holds the address of the table of
            memory regions.

        :param int p: The ID of the processor to get the user 0 address from
        :param int user: The user number to get the address for
        :return: The address for user 0 register for this processor
        :rtype: int
        """
        if user < 0 or user > CPU_MAX_USER:
            raise ValueError(
                f"Incorrect user number {user}")
        return (get_vcpu_address(p) + CPU_USER_START_ADDRESS +
                CPU_USER_OFFSET * user)

    def read_user(self, x, y, p, user):
        """
        Get the contents of the this user register for the given processor.

        .. note::
            Conventionally, user_0 usually holds the address of the table of
            memory regions.

        :param int x: X coordinate of the chip
        :param int y: Y coordinate of the chip
        :param int p: Virtual processor identifier on the chip
        :param int user: The user number to read data for
        :rtype: int
        :raise SpinnmanIOException:
            If there is an error communicating with the board
        :raise SpinnmanInvalidPacketException:
            If a packet is received that is not in the valid format
        :raise SpinnmanInvalidParameterException:
            If x, y, p does not identify a valid processor
        :raise SpinnmanUnexpectedResponseCodeException:
            If a response indicates an error during the exchange
        """
        addr = self.__get_user_register_address_from_core(p, user)
        return self.read_word(x, y, addr)

    def get_cpu_information_from_core(self, x, y, p):
        """
        Get information about a specific processor on the board.

        :param int x: The x-coordinate of the chip containing the processor
        :param int y: The y-coordinate of the chip containing the processor
        :param int p: The ID of the processor to get the information about
        :return: The CPU information for the selected core
        :rtype: CPUInfo
        :raise SpinnmanIOException:
            If there is an error communicating with the board
        :raise SpinnmanInvalidPacketException:
            If a packet is received that is not in the valid format
        :raise SpinnmanInvalidParameterException:
            * If x, y, p is not a valid processor
            * If a packet is received that has invalid parameters
        :raise SpinnmanUnexpectedResponseCodeException:
            If a response indicates an error during the exchange
        """
        core_subsets = CoreSubsets()
        core_subsets.add_processor(x, y, p)
        cpu_infos = self.get_cpu_infos(core_subsets)
        return cpu_infos.get_cpu_info(x, y, p)

    def get_iobuf(self, core_subsets=None):
        """
        Get the contents of the IOBUF buffer for a number of processors.

        :param ~spinn_machine.CoreSubsets core_subsets:
            A set of chips and cores from which to get the buffers. If not
            specified, the buffers from all of the cores on all of the chips
            on the board are obtained.
        :return: An iterable of the buffers, which may not be in the order
            of core_subsets
        :rtype: iterable(IOBuffer)
        :raise SpinnmanIOException:
            If there is an error communicating with the board
        :raise SpinnmanInvalidPacketException:
            If a packet is received that is not in the valid format
        :raise SpinnmanInvalidParameterException:
            * If chip_and_cores contains invalid items
            * If a packet is received that has invalid parameters
        :raise SpinnmanUnexpectedResponseCodeException:
            If a response indicates an error during the exchange
        """
        # making the assumption that all chips have the same iobuf size.
        if self._iobuf_size is None:
            self._iobuf_size = self._get_sv_data(
                AbstractSCPRequest.DEFAULT_DEST_X_COORD,
                AbstractSCPRequest.DEFAULT_DEST_Y_COORD,
                SystemVariableDefinition.iobuf_size)

        # read iobuf from machine
        process = ReadIOBufProcess(self._scamp_connection_selector)
        return process.read_iobuf(self._iobuf_size, core_subsets)

    def get_core_state_count(self, app_id, state):
        """
        Get a count of the number of cores which have a given state.

        :param int app_id:
            The ID of the application from which to get the count.
        :param CPUState state: The state count to get
        :return: A count of the cores with the given status
        :rtype: int
        :raise SpinnmanIOException:
            If there is an error communicating with the board
        :raise SpinnmanInvalidPacketException:
            If a packet is received that is not in the valid format
        :raise SpinnmanInvalidParameterException:
            * If state is not a valid status
            * If app_id is not a valid application ID
            * If a packet is received that has invalid parameters
        :raise SpinnmanUnexpectedResponseCodeException:
            If a response indicates an error during the exchange
        """
        process = SendSingleCommandProcess(self._scamp_connection_selector)
        response = process.execute(CountState(app_id, state))
        return response.count  # pylint: disable=no-member

    def execute_flood(
            self, core_subsets, executable, app_id, n_bytes=None, wait=False,
            is_filename=False):
        """
        Start an executable running on multiple places on the board.  This
        will be optimised based on the selected cores, but it may still
        require a number of communications with the board to execute.

        :param ~spinn_machine.CoreSubsets core_subsets:
            Which cores on which chips to start the executable
        :param executable:
            The data that is to be executed. Should be one of the following:

            * An instance of RawIOBase
            * A bytearray
            * A filename of an executable (in which case `is_filename` must be
              set to True)
        :type executable:
            ~io.RawIOBase or bytes or bytearray or str
        :param int app_id:
            The ID of the application with which to associate the executable
        :param int n_bytes:
            The size of the executable data in bytes. If not specified:

            * If `executable` is an RawIOBase, an error is raised
            * If `executable` is a bytearray, the length of the bytearray will
              be used
            * If `executable` is an int, 4 will be used
            * If `executable` is a str, the length of the file will be used
        :param bool wait:
            True if the processors should enter a "wait" state on loading
        :param bool is_filename: True if the data is a filename
        :raise SpinnmanIOException:
            * If there is an error communicating with the board
            * If there is an error reading the executable
        :raise SpinnmanInvalidPacketException:
            If a packet is received that is not in the valid format
        :raise SpinnmanInvalidParameterException:
            * If one of the specified cores is not valid
            * If `app_id` is an invalid application ID
            * If a packet is received that has invalid parameters
            * If `executable` is an RawIOBase but `n_bytes` is not specified
            * If `executable` is an int and `n_bytes` is more than 4
            * If `n_bytes` is less than 0
        :raise SpinnmanUnexpectedResponseCodeException:
            If a response indicates an error during the exchange
        """
        # Lock against other executable's
        with self.__flood_execute_lock():
            # Flood fill the system with the binary
            n_bytes, chksum = self.write_memory(
                0, 0, _EXECUTABLE_ADDRESS, executable, n_bytes,
                is_filename=is_filename, get_sum=True)

            # Execute the binary on the cores on 0, 0 if required
            if core_subsets.is_chip(0, 0):
                boot_subset = CoreSubsets()
                boot_subset.add_core_subset(
                    core_subsets.get_core_subset_for_chip(0, 0))
                process = ApplicationRunProcess(
                    self._scamp_connection_selector)
                process.run(app_id, boot_subset, wait)

            process = ApplicationCopyRunProcess(
                self._scamp_connection_selector)
            process.run(n_bytes, app_id, core_subsets, chksum, wait)

    def _power_on_machine(self):
        """
        Power on the whole machine.

        :rtype bool
        :return success of failure to power on machine
        """
        if self._bmp_connection is None:
            logger.warning("No BMP connections, so can't power on")
            return False
        self.power_on(self._bmp_connection)
        return True

    def power_on(self, boards=0):
        """
        Power on a set of boards in the machine.

        :param int boards: The board or boards to power on
        """
        self._power(PowerCommand.POWER_ON, boards)

    def power_off_machine(self):
        """
        Power off the whole machine.

        :rtype bool
        :return success or failure to power off the machine
        """
        if self._bmp_connection is None:
            logger.warning("No BMP connections, so can't power off")
            return False
        logger.info("Turning off machine")
        self.power_off(self._bmp_connection)
        return True

    def power_off(self, boards=0):
        """
        Power off a set of boards in the machine.

        :param int boards: The board or boards to power off
        """
        self._power(PowerCommand.POWER_OFF, boards)

    def _power(self, power_command, boards=0):
        """
        Send a power request to the machine.

        :param PowerCommand power_command: The power command to send
        :param boards: The board or boards to send the command to
        """
        connection_selector = self._bmp_selector
        timeout = (
            BMP_POWER_ON_TIMEOUT
            if power_command == PowerCommand.POWER_ON
            else BMP_TIMEOUT)
        process = SendSingleCommandProcess(
            connection_selector, timeout=timeout, n_retries=0)
        process.execute(SetPower(power_command, boards))
        self._machine_off = power_command == PowerCommand.POWER_OFF

        # Sleep for 5 seconds if the machine has just been powered on
        if not self._machine_off:
            time.sleep(BMP_POST_POWER_ON_SLEEP_TIME)

    def read_fpga_register(
            self, fpga_num, register, board=0):
        """
        Read a register on a FPGA of a board. The meaning of the
        register's contents will depend on the FPGA's configuration.

        :param int fpga_num: FPGA number (0, 1 or 2) to communicate with.
        :param int register:
            Register address to read to (will be rounded down to
            the nearest 32-bit word boundary).
        :param int board: which board to request the FPGA register from
        :return: the register data
        :rtype: int
        """
        process = SendSingleCommandProcess(self._bmp_selector, timeout=1.0)
        response = process.execute(
            ReadFPGARegister(fpga_num, register, board))
        return response.fpga_register  # pylint: disable=no-member

    def write_fpga_register(self, fpga_num, register, value, board=0):
        """
        Write a register on a FPGA of a board. The meaning of setting the
        register's contents will depend on the FPGA's configuration.

        :param int fpga_num: FPGA number (0, 1 or 2) to communicate with.
        :param int register:
            Register address to read to (will be rounded down to
            the nearest 32-bit word boundary).
        :param int value: the value to write into the FPGA register
        :param int board: which board to write the FPGA register to
        """
        process = SendSingleCommandProcess(self._bmp_selector)
        process.execute(
            WriteFPGARegister(fpga_num, register, value, board))

    def read_bmp_version(self, board):
        """
        Read the BMP version.

        :param int board: which board to request the data from
        :return: the sver from the BMP
        """
        process = SendSingleCommandProcess(self._bmp_selector)
        response = process.execute(BMPGetVersion(board))
        return response.version_info  # pylint: disable=no-member

    def write_memory(self, x, y, base_address, data, n_bytes=None, offset=0,
                     cpu=0, is_filename=False, get_sum=False):
        """
        Write to the SDRAM on the board.

        :param int x:
            The x-coordinate of the chip where the memory is to be written to
        :param int y:
            The y-coordinate of the chip where the memory is to be written to
        :param int base_address:
            The address in SDRAM where the region of memory is to be written
        :param data: The data to write.  Should be one of the following:

            * An instance of RawIOBase
            * A bytearray/bytes
            * A single integer - will be written in little-endian byte order
            * A filename of a data file (in which case `is_filename` must be
              set to True)
        :type data:
            ~io.RawIOBase or bytes or bytearray or int or str
        :param int n_bytes:
            The amount of data to be written in bytes.  If not specified:

            * If `data` is an RawIOBase, an error is raised
            * If `data` is a bytearray, the length of the bytearray will be
              used
            * If `data` is an int, 4 will be used
            * If `data` is a str, the length of the file will be used
        :param int offset: The offset from which the valid data begins
        :param int cpu: The optional CPU to write to
        :param bool is_filename: True if `data` is a filename
        :param bool get_sum: whether to return a checksum or 0
        :return: The number of bytes written, the checksum (0 if get_sum=False)
        :rtype: int, int
        :raise SpinnmanIOException:
            * If there is an error communicating with the board
            * If there is an error reading the data
        :raise SpinnmanInvalidPacketException:
            If a packet is received that is not in the valid format
        :raise SpinnmanInvalidParameterException:
            * If `x, y` does not lead to a valid chip
            * If a packet is received that has invalid parameters
            * If `base_address` is not a positive integer
            * If `data` is an RawIOBase but `n_bytes` is not specified
            * If `data` is an int and `n_bytes` is more than 4
            * If `n_bytes` is less than 0
        :raise SpinnmanUnexpectedResponseCodeException:
            If a response indicates an error during the exchange
        """
        process = WriteMemoryProcess(self._scamp_connection_selector)
        if isinstance(data, io.RawIOBase):
            chksum = process.write_memory_from_reader(
                x, y, cpu, base_address, data, n_bytes, get_sum)
        elif isinstance(data, str) and is_filename:
            if n_bytes is None:
                n_bytes = os.stat(data).st_size
            with open(data, "rb") as reader:
                chksum = process.write_memory_from_reader(
                    x, y, cpu, base_address, reader, n_bytes, get_sum)
        elif isinstance(data, int):
            n_bytes = 4
            data_to_write = _ONE_WORD.pack(data)
            chksum = process.write_memory_from_bytearray(
                x, y, cpu, base_address, data_to_write, 0, n_bytes, get_sum)
        else:
            if n_bytes is None:
                n_bytes = len(data)
            chksum = process.write_memory_from_bytearray(
                x, y, cpu, base_address, data, offset, n_bytes, get_sum)
        return n_bytes, chksum

    def write_user(self, x, y, p, user, value):
        """
        Write to the this user register for the given processor.

        .. note::
            Conventionally, user_0 usually holds the address of the table of
            memory regions.

        :param int x: X coordinate of the chip
        :param int y: Y coordinate of the chip
        :param int p: Virtual processor identifier on the chip
        :param int user: The user number of write data for
        :param int value: The value to write
        :raise SpinnmanIOException:
            If there is an error communicating with the board
        :raise SpinnmanInvalidPacketException:
            If a packet is received that is not in the valid format
        :raise SpinnmanInvalidParameterException:
            If x, y, p does not identify a valid processor
        :raise SpinnmanUnexpectedResponseCodeException:
            If a response indicates an error during the exchange
        """
        addr = self.__get_user_register_address_from_core(p, user)
        self.write_memory(x, y, addr, int(value))

    def read_memory(self, x, y, base_address, length, cpu=0):
        """
        Read some areas of memory (usually SDRAM) from the board.

        :param int x:
            The x-coordinate of the chip where the memory is to be read from
        :param int y:
            The y-coordinate of the chip where the memory is to be read from
        :param int base_address:
            The address in SDRAM where the region of memory to be read starts
        :param int length: The length of the data to be read in bytes
        :param int cpu:
            the core ID used to read the memory of; should usually be 0 when
            reading from SDRAM, but may be other values when reading from DTCM.
        :return: A bytearray of data read
        :rtype: bytes
        :raise SpinnmanIOException:
            If there is an error communicating with the board
        :raise SpinnmanInvalidPacketException:
            If a packet is received that is not in the valid format
        :raise SpinnmanInvalidParameterException:
            * If one of `x`, `y`, `cpu`, `base_address` or `length` is invalid
            * If a packet is received that has invalid parameters
        :raise SpinnmanUnexpectedResponseCodeException:
            If a response indicates an error during the exchange
        """
        try:
            process = ReadMemoryProcess(self._scamp_connection_selector)
            return process.read_memory(x, y, cpu, base_address, length)
        except Exception:
            logger.info(self._where_is_xy(x, y))
            raise

    def read_word(self, x, y, base_address, cpu=0):
        """
        Read a word (usually of SDRAM) from the board.

        :param int x:
            The x-coordinate of the chip where the word is to be read from
        :param int y:
            The y-coordinate of the chip where the word is to be read from
        :param int base_address:
            The address (usually in SDRAM) where the word to be read starts
        :param int cpu:
            the core ID used to read the word; should usually be 0 when reading
            from SDRAM, but may be other values when reading from DTCM.
        :return: The unsigned integer value at ``base_address``
        :rtype: int
        :raise SpinnmanIOException:
            If there is an error communicating with the board
        :raise SpinnmanInvalidPacketException:
            If a packet is received that is not in the valid format
        :raise SpinnmanInvalidParameterException:
            * If one of `x`, `y`, `cpu` or `base_address` is invalid
            * If a packet is received that has invalid parameters
        :raise SpinnmanUnexpectedResponseCodeException:
            If a response indicates an error during the exchange
        """
        try:
            process = ReadMemoryProcess(self._scamp_connection_selector)
            data = process.read_memory(x, y, cpu, base_address, _ONE_WORD.size)
            (value, ) = _ONE_WORD.unpack(data)
            return value
        except Exception:
            logger.info(self._where_is_xy(x, y))
            raise

    def stop_application(self, app_id):
        """
        Sends a stop request for an app_id.

        :param int app_id: The ID of the application to send to
        :raise SpinnmanIOException:
            If there is an error communicating with the board
        :raise SpinnmanInvalidPacketException:
            If a packet is received that is not in the valid format
        :raise SpinnmanInvalidParameterException:
            * If app_id is not a valid application ID
            * If a packet is received that has invalid parameters
        :raise SpinnmanUnexpectedResponseCodeException:
            If a response indicates an error during the exchange
        """

        if not self._machine_off:
            process = SendSingleCommandProcess(self._scamp_connection_selector)
            process.execute(AppStop(app_id))
        else:
            logger.warning(
                "You are calling a app stop on a turned off machine. "
                "Please fix and try again")

    def __log_where_is_info(self, cpu_infos):
        """
        Logs the where_is info for each chip in cpu_infos.

        :param cpu_infos:
        """
        xys = set()
        for cpu_info in cpu_infos:
            if isinstance(cpu_info, tuple):
                xys.add((cpu_info[0], cpu_info[1]))
            else:
                xys.add((cpu_info.x, cpu_info.y))
        for (x, y) in xys:
            logger.info(self._where_is_xy(x, y))

    def wait_for_cores_to_be_in_state(
            self, all_core_subsets, app_id, cpu_states, timeout=None,
            time_between_polls=0.1,
            error_states=frozenset({
                CPUState.RUN_TIME_EXCEPTION, CPUState.WATCHDOG}),
            counts_between_full_check=100, progress_bar=None):
        """
        Waits for the specified cores running the given application to be
        in some target state or states. Handles failures.

        :param ~spinn_machine.CoreSubsets all_core_subsets:
            the cores to check are in a given sync state
        :param int app_id: the application ID that being used by the simulation
        :param set(CPUState) cpu_states:
            The expected states once the applications are ready; success is
            when each application is in one of these states
        :param float timeout:
            The amount of time to wait in seconds for the cores to reach one
            of the states
        :param float time_between_polls: Time between checking the state
        :param set(CPUState) error_states:
            Set of states that the application can be in that indicate an
            error, and so should raise an exception
        :param int counts_between_full_check:
            The number of times to use the count signal before instead using
            the full CPU state check
        :param progress_bar: Possible progress bar to update.
        :type progress_bar: ~spinn_utilities.progress_bar.ProgressBar or None
        :raise SpinnmanTimeoutException:
            If a timeout is specified and exceeded.
        """
        # check that the right number of processors are in the states
        processors_ready = 0
        max_processors_ready = 0
        timeout_time = None if timeout is None else time.time() + timeout
        tries = 0
        while (processors_ready < len(all_core_subsets) and
               (timeout_time is None or time.time() < timeout_time)):

            # Get the number of processors in the ready states
            processors_ready = 0
            for cpu_state in cpu_states:
                processors_ready += self.get_core_state_count(
                    app_id, cpu_state)
            if progress_bar:
                if processors_ready > max_processors_ready:
                    progress_bar.update(
                        processors_ready - max_processors_ready)
                    max_processors_ready = processors_ready
            # If the count is too small, check for error states
            if processors_ready < len(all_core_subsets):
                is_error = False
                for cpu_state in error_states:
                    error_cores = self.get_core_state_count(app_id, cpu_state)
                    if error_cores > 0:
                        is_error = True
                if is_error:
                    error_core_states = self.get_cpu_infos(
                        all_core_subsets, error_states, True)
                    if len(error_core_states) > 0:
                        self.__log_where_is_info(error_core_states)
                        raise SpiNNManCoresNotInStateException(
                            timeout, cpu_states, error_core_states)

                # If we haven't seen an error, increase the tries, and
                # do a full check if required
                tries += 1
                if tries >= counts_between_full_check:
                    cores_in_state = self.get_cpu_infos(
                        all_core_subsets, cpu_states, True)
                    processors_ready = len(cores_in_state)
                    tries = 0

                    # iterate over the cores waiting to finish and see
                    # which ones we're missing
                    if get_config_bool("Machine", "report_waiting_logs"):
                        for core_subset in all_core_subsets.core_subsets:
                            for p in core_subset.processor_ids:
                                if ((core_subset.x, core_subset.y, p) not in
                                        cores_in_state.keys()):
                                    logger.warning(
                                        "waiting on {}:{}:{}",
                                        core_subset.x, core_subset.y, p)

                # If we're still not in the correct state, wait a bit
                if processors_ready < len(all_core_subsets):
                    time.sleep(time_between_polls)

        # If we haven't reached the final state, do a final full check
        if processors_ready < len(all_core_subsets):
            cores_not_in_state = self.get_cpu_infos(
                all_core_subsets, cpu_states, False)

            # If we are sure we haven't reached the final state,
            # report a timeout error
            if len(cores_not_in_state) != 0:
                self.__log_where_is_info(cores_not_in_state)
                raise SpiNNManCoresNotInStateException(
                    timeout, cpu_states, cores_not_in_state)

    def send_signal(self, app_id, signal):
        """
        Send a signal to an application.

        :param int app_id: The ID of the application to send to
        :param ~spinnman.messages.scp.enums.Signal signal: The signal to send
        :raise SpinnmanIOException:
            If there is an error communicating with the board
        :raise SpinnmanInvalidPacketException:
            If a packet is received that is not in the valid format
        :raise SpinnmanInvalidParameterException:
            * If signal is not a valid signal
            * If app_id is not a valid application ID
            * If a packet is received that has invalid parameters
        :raise SpinnmanUnexpectedResponseCodeException:
            If a response indicates an error during the exchange
        """
        process = SendSingleCommandProcess(self._scamp_connection_selector)
        process.execute(SendSignal(app_id, signal))

    def _locate_spinnaker_connection_for_board_address(self, board_address):
        """
        Find a connection that matches the given board IP address.

        :param str board_address:
            The IP address of the Ethernet connection on the board
        :return: A connection for the given IP address, or `None` if no such
            connection exists
        :rtype: SCAMPConnection
        """
        return self._udp_scamp_connections.get(board_address, None)

    def set_ip_tag(self, ip_tag, use_sender=False):
        """
        Set up an IP tag.

        :param ~spinn_machine.tags.IPTag ip_tag:
            The tag to set up.

            .. note::
                `board_address` can be `None`, in which case, the tag will be
                assigned to all boards.
        :param bool use_sender:
            Optionally use the sender host and port instead of
            the given host and port in the tag
        :raise SpinnmanIOException:
            If there is an error communicating with the board
        :raise SpinnmanInvalidPacketException:
            If a packet is received that is not in the valid format
        :raise SpinnmanInvalidParameterException:
            * If the IP tag fields are incorrect
            * If a packet is received that has invalid parameters
        :raise SpinnmanUnexpectedResponseCodeException:
            If a response indicates an error during the exchange
        """
        # Check that the tag has a port assigned
        if ip_tag.port is None:
            raise SpinnmanInvalidParameterException(
                "ip_tag.port", "None", "The tag port must have been set")

        # Get the connections - if the tag specifies a connection, use that,
        # otherwise apply the tag to all connections
        connections = self.__get_connection_list(None, ip_tag.board_address)
        if not connections:
            raise SpinnmanInvalidParameterException(
                "ip_tag", str(ip_tag),
                "The given board address is not recognised")

        for connection in connections:
            # Convert the host string
            host_string = ip_tag.ip_address
            if host_string in ("localhost", ".", "0.0.0.0"):
                host_string = connection.local_ip_address
            ip_string = socket.gethostbyname(host_string)
            ip_address = bytearray(socket.inet_aton(ip_string))

            process = SendSingleCommandProcess(self._scamp_connection_selector)
            process.execute(IPTagSet(
                connection.chip_x, connection.chip_y, ip_address, ip_tag.port,
                ip_tag.tag, strip=ip_tag.strip_sdp, use_sender=use_sender))

    def __get_connection_list(self, connection=None, board_address=None):
        """
        Get the connections for talking to a board.

        :param SCAMPConnection connection:
            Optional param that directly gives the connection to use.
        :param str board_address:
            Optional param that gives the address of the board to talk to.
        :return: List of length 1 or 0 (the latter only if the search for
            the given board address fails).
        :rtype: list(SCAMPConnection)
        """
        if connection is not None:
            return [connection]
        elif board_address is None:
            return self._scamp_connections

        connection = self._locate_spinnaker_connection_for_board_address(
            board_address)
        if connection is None:
            return []
        return [connection]

    def set_reverse_ip_tag(self, reverse_ip_tag):
        """
        Set up a reverse IP tag.

        :param ~spinn_machine.tags.ReverseIPTag reverse_ip_tag:
            The reverse tag to set up.

            .. note::
                The `board_address` field can be `None`, in which case, the tag
                will be assigned to all boards.
        :raise SpinnmanIOException:
            If there is an error communicating with the board
        :raise SpinnmanInvalidPacketException:
            If a packet is received that is not in the valid format
        :raise SpinnmanInvalidParameterException:
            * If the reverse IP tag fields are incorrect
            * If a packet is received that has invalid parameters
            * If the UDP port is one that is already used by SpiNNaker for
                system functions
        :raise SpinnmanUnexpectedResponseCodeException:
            If a response indicates an error during the exchange
        """
        if reverse_ip_tag.port is None:
            raise SpinnmanInvalidParameterException(
                "reverse_ip_tag.port", "None",
                "The tag port must have been set!")

        if (reverse_ip_tag.port == SCP_SCAMP_PORT or
                reverse_ip_tag.port == UDP_BOOT_CONNECTION_DEFAULT_PORT):
            raise SpinnmanInvalidParameterException(
                "reverse_ip_tag.port", reverse_ip_tag.port,
                "The port number for the reverse IP tag conflicts with"
                f" the SpiNNaker system ports ({SCP_SCAMP_PORT} and "
                f"{UDP_BOOT_CONNECTION_DEFAULT_PORT})")

        # Get the connections - if the tag specifies a connection, use that,
        # otherwise apply the tag to all connections
        connections = self.__get_connection_list(
            None, reverse_ip_tag.board_address)
        if not connections:
            raise SpinnmanInvalidParameterException(
                "reverse_ip_tag", str(reverse_ip_tag),
                "The given board address is not recognised")

        for connection in connections:
            process = SendSingleCommandProcess(self._scamp_connection_selector)
            process.execute(ReverseIPTagSet(
                connection.chip_x, connection.chip_y,
                reverse_ip_tag.destination_x, reverse_ip_tag.destination_y,
                reverse_ip_tag.destination_p,
                reverse_ip_tag.port, reverse_ip_tag.tag,
                reverse_ip_tag.sdp_port))

    def clear_ip_tag(self, tag, board_address=None):
        """
        Clear the setting of an IP tag.

        :param int tag: The tag ID
        :param str board_address:
            Board address where the tag should be cleared.
            If not specified, all AbstractSCPConnection connections will send
            the message to clear the tag
        :raise SpinnmanIOException:
            If there is an error communicating with the board
        :raise SpinnmanInvalidPacketException:
            If a packet is received that is not in the valid format
        :raise SpinnmanInvalidParameterException:
            * If the tag is not a valid tag
            * If the connection cannot send SDP messages
            * If a packet is received that has invalid parameters
        :raise SpinnmanUnexpectedResponseCodeException:
            If a response indicates an error during the exchange
        """
        for conn in self.__get_connection_list(board_address=board_address):
            process = SendSingleCommandProcess(self._scamp_connection_selector)
            process.execute(IPTagClear(conn.chip_x, conn.chip_y, tag))

    def get_tags(self, connection=None):
        """
        Get the current set of tags that have been set on the board.

        :param AbstractSCPConnection connection:
            Connection from which the tags should be received.
            If not specified, all AbstractSCPConnection connections will be
            queried and the response will be combined.
        :return: An iterable of tags
        :rtype: iterable(~spinn_machine.tags.AbstractTag)
        :raise SpinnmanIOException:
            If there is an error communicating with the board
        :raise SpinnmanInvalidPacketException:
            If a packet is received that is not in the valid format
        :raise SpinnmanInvalidParameterException:
            * If the connection cannot send SDP messages
            * If a packet is received that has invalid parameters
        :raise SpinnmanUnexpectedResponseCodeException:
            If a response indicates an error during the exchange
        """
        all_tags = list()
        for conn in self.__get_connection_list(connection):
            process = GetTagsProcess(self._scamp_connection_selector)
            all_tags.extend(process.get_tags(conn))
        return all_tags

    def malloc_sdram(self, x, y, size, app_id, tag=None):
        """
        Allocates a chunk of SDRAM on a chip on the machine.

        :param int x: The x-coordinate of the chip onto which to ask for memory
        :param int y: The y-coordinate of the chip onto which to ask for memory
        :param int size: the amount of memory to allocate in bytes
        :param int app_id: The ID of the application with which to associate
            the routes.  If not specified, defaults to 0.
        :param int tag: the tag for the SDRAM, a 8-bit (chip-wide) tag that can
            be looked up by a SpiNNaker application to discover the address of
            the allocated block. If `0` then no tag is applied.
        :return: the base address of the allocated memory
        :rtype: int
        """
        try:
            process = MallocSDRAMProcess(self._scamp_connection_selector)
            process.malloc_sdram(x, y, size, app_id, tag)
            return process.base_address
        except Exception:
            logger.info(self._where_is_xy(x, y))
            raise

    def load_multicast_routes(self, x, y, routes, app_id):
        """
        Load a set of multicast routes on to a chip.

        :param int x:
            The x-coordinate of the chip onto which to load the routes
        :param int y:
            The y-coordinate of the chip onto which to load the routes
        :param iterable(~spinn_machine.MulticastRoutingEntry) routes:
            An iterable of multicast routes to load
        :param int app_id: The ID of the application with which to associate
            the routes.  If not specified, defaults to 0.
        :raise SpinnmanIOException:
            If there is an error communicating with the board
        :raise SpinnmanInvalidPacketException:
            If a packet is received that is not in the valid format
        :raise SpinnmanInvalidParameterException:
            * If any of the routes are invalid
            * If a packet is received that has invalid parameters
        :raise SpinnmanUnexpectedResponseCodeException:
            If a response indicates an error during the exchange
        """
        try:
            process = LoadMultiCastRoutesProcess(
                self._scamp_connection_selector)
            process.load_routes(x, y, routes, app_id)
        except Exception:
            logger.info(self._where_is_xy(x, y))
            raise

    def load_fixed_route(self, x, y, fixed_route, app_id):
        """
        Loads a fixed route routing table entry onto a chip's router.

        :param int x:
            The x-coordinate of the chip onto which to load the routes
        :param int y:
            The y-coordinate of the chip onto which to load the routes
        :param ~spinn_machine.FixedRouteEntry fixed_route:
            the route for the fixed route entry on this chip
        :param int app_id: The ID of the application with which to associate
            the routes.  If not specified, defaults to 0.
        :raise SpinnmanIOException:
            If there is an error communicating with the board
        :raise SpinnmanInvalidPacketException:
            If a packet is received that is not in the valid format
        :raise SpinnmanInvalidParameterException:
            * If any of the routes are invalid
            * If a packet is received that has invalid parameters
        :raise SpinnmanUnexpectedResponseCodeException:
            If a response indicates an error during the exchange
        """
        try:
            process = LoadFixedRouteRoutingEntryProcess(
                self._scamp_connection_selector)
            process.load_fixed_route(x, y, fixed_route, app_id)
        except Exception:
            logger.info(self._where_is_xy(x, y))
            raise

    def read_fixed_route(self, x, y, app_id):
        """
        Reads a fixed route routing table entry from a chip's router.

        :param int x:
            The x-coordinate of the chip onto which to load the routes
        :param int y:
            The y-coordinate of the chip onto which to load the routes
        :param int app_id:
            The ID of the application with which to associate the
            routes.  If not specified, defaults to 0.
        :return: the route as a fixed route entry
        """
        try:
            process = ReadFixedRouteRoutingEntryProcess(
                self._scamp_connection_selector)
            return process.read_fixed_route(x, y, app_id)
        except Exception:
            logger.info(self._where_is_xy(x, y))
            raise

    def get_multicast_routes(self, x, y, app_id=None):
        """
        Get the current multicast routes set up on a chip.

        :param int x:
            The x-coordinate of the chip from which to get the routes
        :param int y:
            The y-coordinate of the chip from which to get the routes
        :param int app_id:
            The ID of the application to filter the routes for. If
            not specified, will return all routes
        :return: An iterable of multicast routes
        :rtype: list(~spinn_machine.MulticastRoutingEntry)
        :raise SpinnmanIOException:
            If there is an error communicating with the board
        :raise SpinnmanInvalidPacketException:
            If a packet is received that is not in the valid format
        :raise SpinnmanInvalidParameterException:
            If a packet is received that has invalid parameters
        :raise SpinnmanUnexpectedResponseCodeException:
            If a response indicates an error during the exchange
        """
        try:
            base_address = self._get_sv_data(
                x, y, SystemVariableDefinition.router_table_copy_address)
            process = GetMultiCastRoutesProcess(
                self._scamp_connection_selector, app_id)
            return process.get_routes(x, y, base_address)
        except Exception:
            logger.info(self._where_is_xy(x, y))
            raise

    def clear_multicast_routes(self, x, y):
        """
        Remove all the multicast routes on a chip.

        :param int x: The x-coordinate of the chip on which to clear the routes
        :param int y: The y-coordinate of the chip on which to clear the routes
        :raise SpinnmanIOException:
            If there is an error communicating with the board
        :raise SpinnmanInvalidPacketException:
            If a packet is received that is not in the valid format
        :raise SpinnmanInvalidParameterException:
            If a packet is received that has invalid parameters
        :raise SpinnmanUnexpectedResponseCodeException:
            If a response indicates an error during the exchange
        """
        try:
            process = SendSingleCommandProcess(self._scamp_connection_selector)
            process.execute(RouterClear(x, y))
        except Exception:
            logger.info(self._where_is_xy(x, y))
            raise

    def get_router_diagnostics(self, x, y):
        """
        Get router diagnostic information from a chip.

        :param int x:
            The x-coordinate of the chip from which to get the information
        :param int y:
            The y-coordinate of the chip from which to get the information
        :return: The router diagnostic information
        :rtype: RouterDiagnostics
        :raise SpinnmanIOException:
            If there is an error communicating with the board
        :raise SpinnmanInvalidPacketException:
            If a packet is received that is not in the valid format
        :raise SpinnmanInvalidParameterException:
            If a packet is received that has invalid parameters
        :raise SpinnmanUnexpectedResponseCodeException:
            If a response indicates an error during the exchange
        """
        try:
            process = ReadRouterDiagnosticsProcess(
                self._scamp_connection_selector)
            return process.get_router_diagnostics(x, y)
        except Exception:
            logger.info(self._where_is_xy(x, y))
            raise

    def set_router_diagnostic_filter(self, x, y, position, diagnostic_filter):
        """
        Sets a router diagnostic filter in a router.

        :param int x:
            The X address of the router in which this filter is being set.
        :param int y:
            The Y address of the router in which this filter is being set.
        :param int position:
            The position in the list of filters where this filter is to be
            added.
        :param ~spinnman.model.DiagnosticFilter diagnostic_filter:
            The diagnostic filter being set in the placed, between 0 and 15.

            .. note::
                Positions 0 to 11 are used by the default filters,
                and setting these positions will result in a warning.
        :raise SpinnmanIOException:
            * If there is an error communicating with the board
            * If there is an error reading the data
        :raise SpinnmanInvalidPacketException:
            If a packet is received that is not in the valid format
        :raise SpinnmanInvalidParameterException:
            * If x, y does not lead to a valid chip
            * If position is less than 0 or more than 15
        :raise SpinnmanUnexpectedResponseCodeException:
            If a response indicates an error during the exchange
        """
        try:
            self.__set_router_diagnostic_filter(
                x, y, position, diagnostic_filter)
        except Exception:
            logger.info(self._where_is_xy(x, y))
            raise

    def __set_router_diagnostic_filter(
            self, x, y, position, diagnostic_filter):
        data_to_send = diagnostic_filter.filter_word
        if position > NO_ROUTER_DIAGNOSTIC_FILTERS:
            raise SpinnmanInvalidParameterException(
                "position", str(position),
                "the range of the position of a router filter is 0 and 16.")
        if position <= ROUTER_DEFAULT_FILTERS_MAX_POSITION:
            logger.warning(
                "You are planning to change a filter which is set by default. "
                "By doing this, other runs occurring on this machine will be "
                "forced to use this new configuration until the machine is "
                "reset. Please also note that these changes will make the "
                "the reports from ybug not correct. This has been executed "
                "and is trusted that the end user knows what they are doing.")
        memory_position = (
            ROUTER_REGISTER_BASE_ADDRESS + ROUTER_FILTER_CONTROLS_OFFSET +
            position * ROUTER_DIAGNOSTIC_FILTER_SIZE)

        process = SendSingleCommandProcess(self._scamp_connection_selector)
        process.execute(WriteMemory(
            x, y, memory_position, _ONE_WORD.pack(data_to_send)))

    def clear_router_diagnostic_counters(self, x, y):
        """
        Clear router diagnostic information on a chip.

        :param int x: The x-coordinate of the chip
        :param int y: The y-coordinate of the chip
        :raise SpinnmanIOException:
            If there is an error communicating with the board
        :raise SpinnmanInvalidPacketException:
            If a packet is received that is not in the valid format
        :raise SpinnmanInvalidParameterException:
            If a packet is received that has invalid parameters or a counter
            ID is out of range
        :raise SpinnmanUnexpectedResponseCodeException:
            If a response indicates an error during the exchange
        """
        try:
            process = SendSingleCommandProcess(self._scamp_connection_selector)
            # Clear all
            process.execute(WriteMemory(
                x, y, 0xf100002c, _ONE_WORD.pack(0xFFFFFFFF)))
        except Exception:
            logger.info(self._where_is_xy(x, y))
            raise

    def close(self):
        """
        Close the transceiver and any threads that are running.
        """
        if self._bmp_connection is not None:
            if get_config_bool("Machine", "turn_off_machine"):
                self.power_off_machine()

        for connection in self._all_connections:
            connection.close()

    def control_sync(self, do_sync):
        """
        Control the synchronisation of the chips.

        :param bool do_sync: Whether to synchronise or not
        """
        process = SendSingleCommandProcess(self._scamp_connection_selector)
        process.execute(DoSync(do_sync))

    def update_provenance_and_exit(self, x, y, p):
        """
        Sends a command to update prevenance and exit

        :param int x:
            The x-coordinate of the core
        :param int y:
            The y-coordinate of the core
        :param int p:
            The processor on the core
        """
        # Send these signals to make sure the application isn't stuck
        self.send_sdp_message(SDPMessage(
            sdp_header=SDPHeader(
                flags=SDPFlag.REPLY_NOT_EXPECTED,
                destination_port=SDP_PORTS.RUNNING_COMMAND_SDP_PORT.value,
                destination_chip_x=x, destination_chip_y=y, destination_cpu=p),
            data=_ONE_WORD.pack(SDP_RUNNING_MESSAGE_CODES
                                .SDP_UPDATE_PROVENCE_REGION_AND_EXIT.value)))

    def __str__(self):
        addr = self._scamp_connections[0].remote_ip_address
        n = len(self._all_connections)
        return f"transceiver object connected to {addr} with {n} connections"

    def __repr__(self):
        return self.__str__()
