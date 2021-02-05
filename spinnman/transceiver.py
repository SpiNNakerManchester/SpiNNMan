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

# pylint: disable=too-many-arguments
import io
import os
import random
import struct
from threading import Condition, RLock
from collections import defaultdict
import logging
import socket
import time
from spinn_utilities.abstract_context_manager import AbstractContextManager
from spinn_utilities.log import FormatAdapter
from spinn_machine import CoreSubsets
from spinnman.constants import (
    BMP_POST_POWER_ON_SLEEP_TIME, BMP_POWER_ON_TIMEOUT, BMP_TIMEOUT,
    CPU_USER_0_START_ADDRESS, CPU_USER_1_START_ADDRESS,
    CPU_USER_2_START_ADDRESS, CPU_USER_3_START_ADDRESS,
    IPTAG_TIME_OUT_WAIT_TIMES, SCP_SCAMP_PORT, SYSTEM_VARIABLE_BASE_ADDRESS,
    UDP_BOOT_CONNECTION_DEFAULT_PORT, NO_ROUTER_DIAGNOSTIC_FILTERS,
    ROUTER_REGISTER_BASE_ADDRESS, ROUTER_DEFAULT_FILTERS_MAX_POSITION,
    ROUTER_FILTER_CONTROLS_OFFSET, ROUTER_DIAGNOSTIC_FILTER_SIZE, N_RETRIES,
    BOOT_RETRIES)
from spinnman.exceptions import (
    SpinnmanInvalidParameterException, SpinnmanException, SpinnmanIOException,
    SpinnmanTimeoutException, SpinnmanGenericProcessException,
    SpinnmanUnexpectedResponseCodeException, SpinnmanInvalidPacketException,
    SpiNNManCoresNotInStateException)
from spinnman.model import CPUInfos, DiagnosticFilter, MachineDimensions
from spinnman.model.enums import CPUState
from spinnman.messages.scp.impl.get_chip_info import GetChipInfo
from spinn_machine.spinnaker_triad_geometry import SpiNNakerTriadGeometry
from spinnman.messages.spinnaker_boot import (
    SystemVariableDefinition, SpinnakerBootMessages)
from spinnman.messages.scp.enums import Signal, PowerCommand
from spinnman.messages.scp.abstract_messages import AbstractSCPRequest
from spinnman.messages.scp.impl import (
    BMPSetLed, BMPGetVersion, SetPower, ReadADC, ReadFPGARegister,
    WriteFPGARegister, IPTagSetTTO, ReverseIPTagSet, ReadMemory,
    CountState, WriteMemory, SetLED, ApplicationRun, SendSignal, AppStop,
    IPTagSet, IPTagClear, RouterClear)
from spinnman.connections import ConnectionListener
from spinnman.connections.abstract_classes import (
    SpinnakerBootSender, SCPSender, SDPSender,
    MulticastSender, SCPReceiver, Listenable)
from spinnman.connections.udp_packet_connections import (
    BMPConnection, UDPConnection, BootConnection, SCAMPConnection)
from spinnman.processes import (
    DeAllocSDRAMProcess, GetMachineProcess, GetVersionProcess,
    MallocSDRAMProcess, WriteMemoryProcess, ReadMemoryProcess,
    GetCPUInfoProcess, ReadIOBufProcess, ApplicationRunProcess, GetHeapProcess,
    LoadFixedRouteRoutingEntryProcess,
    ReadFixedRouteRoutingEntryProcess, WriteMemoryFloodProcess,
    LoadMultiCastRoutesProcess, GetTagsProcess, GetMultiCastRoutesProcess,
    SendSingleCommandProcess, ReadRouterDiagnosticsProcess,
    MostDirectConnectionSelector)
from spinnman.utilities.utility_functions import (
    get_vcpu_address, work_out_bmp_from_machine_details)
from spinnman.utilities.appid_tracker import AppIdTracker

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


def create_transceiver_from_hostname(
        hostname, version, bmp_connection_data=None, number_of_boards=None,
        ignore_chips=None, ignore_cores=None, ignored_links=None,
        auto_detect_bmp=False, scamp_connections=None,
        boot_port_no=None, max_sdram_size=None, repair_machine=False,
        ignore_bad_ethernets=True, default_report_directory=None,
        report_waiting_logs=False):
    """ Create a Transceiver by creating a :py:class:`~.UDPConnection` to the\
        given hostname on port 17893 (the default SCAMP port), and a\
        :py:class:`~.BootConnection` on port 54321 (the default boot port),\
        optionally discovering any additional links using the UDPConnection,\
        and then returning the transceiver created with the conjunction of\
        the created UDPConnection and the discovered connections.

    :param str hostname: The hostname or IP address of the board
    :param number_of_boards: a number of boards expected to be supported, or
        ``None``, which defaults to a single board
    :type number_of_boards: int or None
    :param set(tuple(int,int)) ignore_chips:
        An optional set of chips to ignore in the machine.
        Requests for a "machine" will have these chips excluded, as if they
        never existed. The processor_ids of the specified chips are ignored.
    :param set(tuple(int,int,int)) ignore_cores:
        An optional set of cores to ignore in the machine.
        Requests for a "machine" will have these cores excluded, as if they
        never existed.
    :param set(tuple(int,int,int)) ignored_links:
        An optional set of links to ignore in the machine.
        Requests for a "machine" will have these links excluded, as if they
        never existed.
    :param int version: the type of SpiNNaker board used within the SpiNNaker
        machine being used. If a spinn-5 board, then the version will be 5,
        spinn-3 would equal 3 and so on.
    :param list(BMPConnectionData) bmp_connection_data:
        the details of the BMP connections used to boot multi-board systems
    :param bool auto_detect_bmp:
        ``True`` if the BMP of version 4 or 5 boards should be
        automatically determined from the board IP address
    :param int boot_port_no: the port number used to boot the machine
    :param list(SCAMPConnection) scamp_connections:
        the list of connections used for SCAMP communications
    :param max_sdram_size:
        the max size each chip can say it has for SDRAM
        (mainly used in debugging purposes)
    :type max_sdram_size: int or None
    :param bool repair_machine:
        Flag to set the behaviour if a repairable error
        is found on the machine.
        If ``True`` will create a machine without the problematic bits.
        (See :py:func:`~spinn_machine.machine_factory.machine_repair`.)
        If ``False`` get machine will raise an Exception if a problematic
        machine is discovered.
    :param bool ignore_bad_ethernets:
        Flag to say that ip_address information
        on non-Ethernet chips should be ignored.
        Non-ethernet chips are defined here as ones that do not report
        themselves as their nearest Ethernet.
        The bad IP address is always logged.
        If ``True`` the IP address is ignored.
        If ``False`` the chip with the bad IP address is removed.
    :param default_report_directory:
        Directory to write any reports too.
        If ``None`` the current directory will be used.
    :type default_report_directory: str or None
    :param report_waiting_logs:  flag for reporting waiting logs
    :type report_waiting_logs: bool
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

    # handle the SpiNNaker connection
    if scamp_connections is None:
        connections.append(SCAMPConnection(remote_host=hostname))

    # handle the boot connection
    connections.append(BootConnection(
        remote_host=hostname, remote_port=boot_port_no))

    return Transceiver(
        version, connections=connections, ignore_chips=ignore_chips,
        ignore_cores=ignore_cores,
        ignore_links=ignored_links, scamp_connections=scamp_connections,
        max_sdram_size=max_sdram_size, repair_machine=repair_machine,
        ignore_bad_ethernets=ignore_bad_ethernets,
        default_report_directory=default_report_directory,
        report_waiting_logs=report_waiting_logs)


class Transceiver(AbstractContextManager):
    """ An encapsulation of various communications with the SpiNNaker board.

    The methods of this class are designed to be thread-safe;
    thus you can make multiple calls to the same (or different) methods
    from multiple threads and expect each call to work as if it had been
    called sequentially, although the order of returns is not guaranteed.

    Note also that with multiple connections to the board, using multiple
    threads in this way may result in an increase in the overall speed of
    operation, since the multiple calls may be made separately over the
    set of given connections.
    """
    __slots__ = [
        "_all_connections",
        "_app_id_tracker",
        "_bmp_connection_selectors",
        "_bmp_connections",
        "_boot_send_connection",
        "_chip_execute_lock_condition",
        "_chip_execute_locks",
        "_default_report_directory",
        "_flood_write_lock",
        "_height",
        "_ignore_bad_ethernets",
        "_ignore_chips",
        "_ignore_cores",
        "_ignore_links",
        "_iobuf_size",
        "_machine",
        "_machine_off",
        "_max_sdram_size",
        "_multicast_sender_connections",
        "_n_chip_execute_locks",
        "_nearest_neighbour_id",
        "_nearest_neighbour_lock",
        "_original_connections",
        "_repair_machine",
        "_scamp_connection_selector",
        "_scamp_connections",
        "_scp_sender_connections",
        "_sdp_sender_connections",
        "_udp_listenable_connections_by_class",
        "_udp_receive_connections_by_port",
        "_udp_scamp_connections",
        "_version",
        "_width",
        "_report_waiting_logs"]

    def __init__(
            self, version, connections=None, ignore_chips=None,
            ignore_cores=None, ignore_links=None,
            scamp_connections=None, max_sdram_size=None, repair_machine=False,
            ignore_bad_ethernets=True, default_report_directory=None,
            report_waiting_logs=False):
        """
        :param int version: The version of the board being connected to
        :param list(Connection) connections:
            An iterable of connections to the board.  If not specified, no
            communication will be possible until connections are found.
        :param set(tuple(int,int)) ignore_chips:
            An optional set of chips to ignore in the machine. Requests for a
            "machine" will have these chips excluded, as if they never
            existed. The processor_ids of the specified chips are ignored.
        :param set(tuple(int,int,int)) ignore_cores:
            An optional set of cores to ignore in the machine. Requests for a
            "machine" will have these cores excluded, as if they never existed.
        :param set(tuple(int,int,int)) ignore_links:
            An optional set of links to ignore in the machine. Requests for a
            "machine" will have these links excluded, as if they never existed.
        :param max_sdram_size: the max size each chip can say it has for SDRAM
            (mainly used in debugging purposes)
        :type max_sdram_size: int or None
        :param list(SocketAddressWithChip) scamp_connections:
            a list of SCAMP connection data or None
        :param bool repair_machine:
            Flag to set the behaviour if a repairable error
            is found on the machine.
            If ``True`` will create a machine without the problematic bits.
            (See :py:func:`~spinn_machine.machine_factory.machine_repair`.)
            If ``False`` get machine will raise an Exception if a problematic
            machine is discovered.
        :param bool ignore_bad_ethernets:
            Flag to say that ip_address information
            on non-Ethernet chips should be ignored.
            Non-Ethernet chips are defined here as ones that do not report
            themselves their nearest Ethernet.
            The bad IP address is always logged.
            If ``True`` the IP address is ignored.
            If ``False`` the chip with the bad IP address is removed.
        :param str default_report_directory:
            Directory to write any reports too. If ``None`` the current
            directory will be used.
        :param report_waiting_logs:  flag for reporting waiting logs
        :type report_waiting_logs: bool
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
        self._machine = None
        self._width = None
        self._height = None
        self._ignore_chips = ignore_chips if ignore_chips is not None else {}
        self._ignore_cores = ignore_cores if ignore_cores is not None else {}
        self._ignore_links = ignore_links if ignore_links is not None else {}
        self._max_sdram_size = max_sdram_size
        self._iobuf_size = None
        self._app_id_tracker = None
        self._repair_machine = repair_machine
        self._ignore_bad_ethernets = ignore_bad_ethernets
        self._report_waiting_logs = report_waiting_logs

        # A set of the original connections - used to determine what can
        # be closed
        if connections is None:
            connections = list()
        self._original_connections = set()
        self._original_connections.update(connections)

        # A set of all connection - used for closing
        self._all_connections = set()
        self._all_connections.update(connections)

        # A boot send connection - there can only be one in the current system,
        # or otherwise bad things can happen!
        self._boot_send_connection = None

        # A dict of port -> dict of IP address -> (connection, listener)
        # for UDP connections.  Note listener might be None if the connection
        # has not been listened to before.
        # Used to keep track of what connection is listening on what port
        # to ensure only one type of traffic is received on any port for any
        # interface
        self._udp_receive_connections_by_port = defaultdict(dict)

        # A dict of class -> list of (connection, listener) for UDP connections
        # that are listenable.  Note that listener might be None if the
        # connection has not be listened to before.
        self._udp_listenable_connections_by_class = defaultdict(list)

        # A list of all connections that can be used to send SCP messages
        # Note that some of these might not be able to receive SCP; this
        # could be useful if they are just using SCP to send a command that
        # doesn't expect a response
        self._scp_sender_connections = list()

        # A list of all connections that can be used to send SDP messages
        self._sdp_sender_connections = list()

        # A list of all connections that can be used to send Multicast messages
        self._multicast_sender_connections = list()

        # A dict of IP address -> SCAMP connection
        # These are those that can be used for setting up IP Tags
        self._udp_scamp_connections = dict()

        # A list of all connections that can be used to send and receive SCP
        # messages for SCAMP interaction
        self._scamp_connections = list()

        # if there has been SCAMP connections given, build them
        if scamp_connections is not None:
            for socket_address in scamp_connections:
                connections.append(SCAMPConnection(
                    remote_host=socket_address.hostname,
                    remote_port=socket_address.port_num,
                    chip_x=socket_address.chip_x,
                    chip_y=socket_address.chip_y))

        # The BMP connections
        self._bmp_connections = list()

        # build connection selectors for the processes.
        self._bmp_connection_selectors = dict()
        self._scamp_connection_selector = \
            self._identify_connections(connections)

        # The nearest neighbour start ID and lock
        self._nearest_neighbour_id = 1
        self._nearest_neighbour_lock = RLock()

        # A lock against multiple flood fill writes - needed as SCAMP cannot
        # cope with this
        self._flood_write_lock = Condition()

        # A lock against single chip executions (entry is (x, y))
        # The condition should be acquired before the locks are
        # checked or updated
        # The write lock condition should also be acquired to avoid a flood
        # fill during an individual chip execute
        self._chip_execute_locks = dict()
        self._chip_execute_lock_condition = Condition()
        self._n_chip_execute_locks = 0

        # Check that the BMP connections are valid
        self._check_bmp_connections()

        self._machine_off = False
        self._default_report_directory = default_report_directory

    def _identify_connections(self, connections):
        for conn in connections:

            # locate the only boot send conn
            if isinstance(conn, SpinnakerBootSender):
                if self._boot_send_connection is not None:
                    raise SpinnmanInvalidParameterException(
                        "connections", "[... {} ...]".format(conn),
                        "Only a single SpinnakerBootSender can be"
                        " specified")
                self._boot_send_connection = conn

            # Locate any connections listening on a UDP port
            if isinstance(conn, UDPConnection):
                self._udp_receive_connections_by_port[conn.local_port][
                    conn.local_ip_address] = (conn, None)
                if isinstance(conn, Listenable):
                    self._udp_listenable_connections_by_class[
                        conn.__class__].append((conn, None))

            # Locate any connections that can send SCP
            # (that are not BMP connections)
            if (isinstance(conn, SCPSender) and
                    not isinstance(conn, BMPConnection)):
                self._scp_sender_connections.append(conn)

            # Locate any connections that can send SDP
            if isinstance(conn, SDPSender):
                self._sdp_sender_connections.append(conn)

            # Locate any connections that can send Multicast
            if isinstance(conn, MulticastSender):
                self._multicast_sender_connections.append(conn)

            # Locate any connections that can send and receive SCP
            if isinstance(conn, SCPSender) and isinstance(conn, SCPReceiver):
                # If it is a BMP conn, add it here
                if isinstance(conn, BMPConnection):
                    self._bmp_connections.append(conn)
                    self._bmp_connection_selectors[conn.cabinet, conn.frame] =\
                        MostDirectConnectionSelector(None, [conn])
                else:
                    self._scamp_connections.append(conn)

                    # If also a UDP conn, add it here (for IP tags)
                    if isinstance(conn, UDPConnection):
                        board_address = conn.remote_ip_address
                        self._udp_scamp_connections[board_address] = conn

        # update the transceiver with the conn selectors.
        return MostDirectConnectionSelector(
            self._machine, self._scamp_connections)

    def _check_bmp_connections(self):
        """ Check that the BMP connections are actually connected to valid BMPs

        :raise SpinnmanIOException: when the conn is not linked to a BMP s
        """
        # check that the UDP BMP conn is actually connected to a BMP
        # via the sver command
        for conn in self._bmp_connections:

            # try to send a BMP sver to check if it responds as expected
            try:
                version_info = self.get_scamp_version(
                    conn.chip_x, conn.chip_y,
                    self._bmp_connection_selectors[conn.cabinet, conn.frame])
                fail_version_name = version_info.name != _BMP_NAME
                fail_version_num = \
                    version_info.version_number[0] not in _BMP_MAJOR_VERSIONS
                if fail_version_name or fail_version_num:
                    raise SpinnmanIOException(
                        "The BMP at {} is running {} {} which is incompatible "
                        "with this transceiver, required version is {} {}"
                        .format(
                            conn.remote_ip_address,
                            version_info.name, version_info.version_string,
                            _BMP_NAME, _BMP_MAJOR_VERSIONS))

                logger.info("Using BMP at {} with version {} {}",
                            conn.remote_ip_address, version_info.name,
                            version_info.version_string)

            # If it fails to respond due to timeout, maybe that the connection
            # isn't valid
            except SpinnmanTimeoutException as e:
                raise SpinnmanException(
                    "BMP connection to {} is not responding".format(
                        conn.remote_ip_address)) from e
            except Exception:
                logger.exception("Failed to speak to BMP at {}",
                                 conn.remote_ip_address)
                raise

    def _check_connection(
            self, connection_selector, chip_x, chip_y):
        """ Check that the given connection to the given chip works

        :param connection_selector: the connection selector to use
        :type connection_selector:
            AbstractMultiConnectionProcessConnectionSelector
        :param int chip_x: the chip x coordinate to try to talk to
        :param int chip_y: the chip y coordinate to try to talk to
        :return: True if a valid response is received, False otherwise
        :rtype: bool
        """
        for _ in range(_CONNECTION_CHECK_RETRIES):
            try:
                sender = SendSingleCommandProcess(connection_selector)
                chip_info = sender.execute(  # pylint: disable=no-member
                    GetChipInfo(chip_x, chip_y)).chip_info
                if not chip_info.is_ethernet_available:
                    time.sleep(0.1)
                else:
                    return True
            except (SpinnmanGenericProcessException, SpinnmanTimeoutException,
                    SpinnmanUnexpectedResponseCodeException):
                pass
            except SpinnmanIOException:
                break
        return False

    def _get_chip_execute_lock(self, x, y):
        """ Get a lock for executing an executable on a chip

        :param int x:
        :param int y:
        """

        key = (x, y)
        # Check if there is a lock for the given chip
        with self._chip_execute_lock_condition:
            if key not in self._chip_execute_locks:
                chip_lock = Condition()
                self._chip_execute_locks[key] = chip_lock
            else:
                chip_lock = self._chip_execute_locks[key]

        # Get the lock for the chip
        chip_lock.acquire()

        # Increment the lock counter (used for the flood lock)
        with self._chip_execute_lock_condition:
            self._n_chip_execute_locks += 1

    def _release_chip_execute_lock(self, x, y):
        """ Release the lock for executing on a chip

        :param int x:
        :param int y:
        """

        # Get the chip lock
        with self._chip_execute_lock_condition:
            chip_lock = self._chip_execute_locks[x, y]

            # Release the chip lock
            chip_lock.release()

            # Decrement the lock and notify
            self._n_chip_execute_locks -= 1
            self._chip_execute_lock_condition.notify_all()

    def _get_flood_execute_lock(self):
        """ Get a lock for executing a flood fill of an executable
        """

        # Get the execute lock all together, so nothing can access it
        self._chip_execute_lock_condition.acquire()

        # Wait until nothing is executing
        while self._n_chip_execute_locks > 0:
            self._chip_execute_lock_condition.wait()

        # When nothing is executing, we can return here

    def _release_flood_execute_lock(self):
        """ Release the lock for executing a flood fill
        """

        # Release the execute lock
        self._chip_execute_lock_condition.release()

    @staticmethod
    def _get_random_connection(connections):
        """ Returns the given connection, or else picks one at random

        :param list(Connection) connections:
            the list of connections to locate a random one from
        :return: a connection object
        :rtype: Connection or None
        """
        if not connections:
            return None
        return connections[random.randint(0, len(connections) - 1)]

    def send_scp_message(self, message, connection=None):
        """ Sends an SCP message, without expecting a response

        :param AbstractSCPRequest message: The message to send
        :param SCAMPConnection connection:
            The connection to use (omit to pick a random one)
        :raise SpinnmanTimeoutException:
            If there is a timeout before a message is received
        :raise SpinnmanInvalidParameterException:
            If one of the fields of the received message is invalid
        :raise SpinnmanInvalidPacketException:
            * If the message is not a recognised packet type
            * If a packet is received that is not a valid response
        :raise SpinnmanUnsupportedOperationException:
            If no connection can send the type of message given
        :raise SpinnmanIOException:
            If there is an error sending the message or receiving the response
        :raise SpinnmanUnexpectedResponseCodeException:
            If the response is not one of the expected codes
        """
        if connection is None:
            connection = self._get_random_connection(
                self._scp_sender_connections)
        connection.send_scp_request(message)

    def send_sdp_message(self, message, connection=None):
        """ Sends an SDP message using one of the connections.

        :param SDPMessage message: The message to send
        :param SDPConnection connection: An optional connection to use
        """
        if connection is None:
            connection_to_use = self._get_random_connection(
                self._sdp_sender_connections)
        else:
            connection_to_use = connection
        connection_to_use.send_sdp_message(message)

    def _update_machine(self):
        """ Get the current machine status and store it
        """

        # Get the width and height of the machine
        self.get_machine_dimensions()

        # Get the coordinates of the boot chip
        version_info = self.get_scamp_version()

        # Get the details of all the chips
        get_machine_process = GetMachineProcess(
            self._scamp_connection_selector, self._ignore_chips,
            self._ignore_cores, self._ignore_links, self._max_sdram_size,
            self._default_report_directory)
        self._machine = get_machine_process.get_machine_details(
            version_info.x, version_info.y, self._width, self._height,
            self._repair_machine, self._ignore_bad_ethernets)

        # update the SCAMP selector with the machine
        self._scamp_connection_selector.set_machine(self._machine)

        # Work out and add the SpiNNaker links and FPGA links
        self._machine.add_spinnaker_links()
        self._machine.add_fpga_links()

        # TODO: Actually get the existing APP_IDs in use
        self._app_id_tracker = AppIdTracker()

        logger.info("Detected a machine on IP address {} which has {}",
                    self._boot_send_connection.remote_ip_address,
                    self._machine.cores_and_link_output_string())

    def discover_scamp_connections(self):
        """ Find connections to the board and store these for future use.\
            Note that connections can be empty, in which case another local\
            discovery mechanism will be used.  Note that an exception will be\
            thrown if no initial connections can be found to the board.

        :return: An iterable of discovered connections, not including the
            initially given connections in the constructor
        :rtype: list(SCAMPConnection)
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
        dims = self.get_machine_dimensions()

        # Find all the new connections via the machine Ethernet-connected chips
        new_connections = list()
        geometry = SpiNNakerTriadGeometry.get_spinn5_geometry()
        for x, y in geometry.get_potential_ethernet_chips(
                dims.width, dims.height):
            ip_addr_item = SystemVariableDefinition.ethernet_ip_address
            ip_address_data = _FOUR_BYTES.unpack_from(
                self.read_memory(
                    x, y,
                    SYSTEM_VARIABLE_BASE_ADDRESS + ip_addr_item.offset, 4))
            ip_address = "{}.{}.{}.{}".format(*ip_address_data)

            if ip_address in self._udp_scamp_connections:
                continue
            conn = self._search_for_proxies(x, y)

            # if no data, no proxy
            if conn is None:
                conn = SCAMPConnection(
                    remote_host=ip_address, chip_x=x, chip_y=y)
            else:
                # proxy, needs an adjustment
                if conn.remote_ip_address in self._udp_scamp_connections:
                    del self._udp_scamp_connections[conn.remote_ip_address]

            # check if it works
            if self._check_connection(
                    MostDirectConnectionSelector(None, [conn]), x, y):
                self._scp_sender_connections.append(conn)
                self._all_connections.add(conn)
                self._udp_scamp_connections[ip_address] = conn
                self._scamp_connections.append(conn)
                new_connections.append(conn)
            else:
                logger.warning(
                    "Additional Ethernet connection on {} at chip {}, {} "
                    "cannot be contacted", ip_address, x, y)

        # Update the connection queues after finding new connections
        return new_connections

    def _search_for_proxies(self, x, y):
        """ Looks for an entry within the UDP SCAMP connections which is\
            linked to a given chip

        :param int x: The x-coordinate of the chip
        :param int y: The y-coordinate of the chip
        :return: the connection to use connection
        :rtype: None or SCAMPConnection
        """
        for connection in self._scamp_connections:
            if connection.chip_x == x and connection.chip_y == y:
                return connection
        return None

    def get_connections(self):
        """ Get the currently known connections to the board, made up of those\
            passed in to the transceiver and those that are discovered during\
            calls to discover_connections.  No further discovery is done here.

        :return: An iterable of connections known to the transceiver
        :rtype: list(Connection)
        """
        return self._all_connections

    def get_machine_dimensions(self):
        """ Get the maximum chip x-coordinate and maximum chip y-coordinate of\
            the chips in the machine

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
        """ Get the details of the machine made up of chips on a board and how\
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
        if self._machine is None:
            self._update_machine()
        return self._machine

    @property
    def app_id_tracker(self):
        """ Get the app ID tracker for this transceiver

        :rtype: AppIdTracker
        """
        if self._app_id_tracker is None:
            self._update_machine()
        return self._app_id_tracker

    def is_connected(self, connection=None):
        """ Determines if the board can be contacted

        :param Connection connection:
            The connection which is to be tested.  If None,
            all connections will be tested, and the board will be considered
            to be connected if any one connection works.
        :return: True if the board can be contacted, False otherwise
        :rtype: bool
        """
        if connection is not None:
            return connection.is_connected()
        return any(c.is_connected() for c in self._scamp_connections)

    def get_scamp_version(
            self, chip_x=AbstractSCPRequest.DEFAULT_DEST_X_COORD,
            chip_y=AbstractSCPRequest.DEFAULT_DEST_Y_COORD,
            connection_selector=None, n_retries=N_RETRIES):
        """ Get the version of SCAMP which is running on the board.

        :param int chip_x: the chip's x coordinate to query for SCAMP version
        :param int chip_y: the chip's y coordinate to query for SCAMP version
        :param connection_selector: the connection to send the SCAMP
            version or none (if none then a random SCAMP connection is used).
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

    def boot_board(
            self, number_of_boards=None, width=None, height=None,
            extra_boot_values=None):
        """ Attempt to boot the board. No check is performed to see if the\
            board is already booted.

        :param number_of_boards: this parameter is deprecated
        :param width: this parameter is deprecated
        :param height: this parameter is deprecated
        :param dict(SystemVariableDefinition,object) extra_boot_values:
            extra values to set during boot
        :raise SpinnmanInvalidParameterException:
            If the board version is not known
        :raise SpinnmanIOException:
            If there is an error communicating with the board
        """
        if (width is not None or height is not None or
                number_of_boards is not None):
            logger.warning(
                "The width, height and number_of_boards are no longer"
                " supported, and might be removed in a future version")
        boot_messages = SpinnakerBootMessages(
            board_version=self._version, extra_boot_values=extra_boot_values)
        for boot_message in boot_messages.messages:
            self._boot_send_connection.send_boot_message(boot_message)
        time.sleep(2.0)

    @staticmethod
    def is_scamp_version_compabible(version):
        """ Determine if the version of SCAMP is compatible with this\
            transceiver

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

    def ensure_board_is_ready(
            self, number_of_boards=None, width=None, height=None,
            n_retries=5, extra_boot_values=None):
        """ Ensure that the board is ready to interact with this version\
            of the transceiver. Boots the board if not already booted and\
            verifies that the version of SCAMP running is compatible with\
            this transceiver.

        :param number_of_boards:
            this parameter is deprecated and will be ignored
        :type number_of_boards: int or None
        :param width: this parameter is deprecated and will be ignored
        :type width: int or None
        :param height: this parameter is deprecated and will be ignored
        :type height: int or None
        :param int n_retries: The number of times to retry booting
        :param dict(SystemVariableDefinition,object) extra_boot_values:
            Any additional values to set during boot
        :return: The version identifier
        :rtype: VersionInfo
        :raise: SpinnmanIOException:
            * If there is a problem booting the board
            * If the version of software on the board is not compatible with\
                this transceiver
        """

        # if the machine sizes not been given, calculate from assumption
        if (width is not None or height is not None or
                number_of_boards is not None):
            logger.warning(
                "The width, height and number_of_boards are no longer"
                " supported, and might be removed in a future version")

        # try to get a SCAMP version once
        logger.info("Working out if machine is booted")
        if self._machine_off:
            version_info = None
        else:
            version_info = self._try_to_find_scamp_and_boot(
                INITIAL_FIND_SCAMP_RETRIES_COUNT, number_of_boards,
                width, height, extra_boot_values)

        # If we fail to get a SCAMP version this time, try other things
        if version_info is None and self._bmp_connections:

            # start by powering up each BMP connection
            logger.info("Attempting to power on machine")
            self.power_on_machine()

            # Sleep a bit to let things get going
            time.sleep(2.0)
            logger.info("Attempting to boot machine")

            # retry to get a SCAMP version, this time trying multiple times
            version_info = self._try_to_find_scamp_and_boot(
                n_retries, number_of_boards, width, height, extra_boot_values)

        # verify that the version is the expected one for this transceiver
        if version_info is None:
            raise SpinnmanIOException(
                "Failed to communicate with the machine")
        if (version_info.name != _SCAMP_NAME or
                not self.is_scamp_version_compabible(
                    version_info.version_number)):
            raise SpinnmanIOException(
                "The machine is currently booted with {}"
                " {} which is incompatible with this transceiver, "
                "required version is {} {}".format(
                    version_info.name, version_info.version_number,
                    _SCAMP_NAME, _SCAMP_VERSION))

        logger.info("Machine communication successful")

        # Change the default SCP timeout on the machine, keeping the old one to
        # revert at close
        for scamp_connection in self._scamp_connections:
            process = SendSingleCommandProcess(self._scamp_connection_selector)
            process.execute(IPTagSetTTO(
                scamp_connection.chip_x, scamp_connection.chip_y,
                IPTAG_TIME_OUT_WAIT_TIMES.TIMEOUT_2560_ms))

        return version_info

    def __is_default_destination(self, version_info):
        return (version_info.x == AbstractSCPRequest.DEFAULT_DEST_X_COORD
                and version_info.y == AbstractSCPRequest.DEFAULT_DEST_Y_COORD)

    def _try_to_find_scamp_and_boot(
            self, tries_to_go, number_of_boards, width, height,
            extra_boot_values):
        """ Try to detect if SCAMP is running, and if not, boot the machine

        :param int tries_to_go: how many attempts should be supported
        :param number_of_boards:
            the number of boards that this machine is built out of;
            this parameter is deprecated
        :param width: The width of the machine in chips;
            this parameter is deprecated
        :param height: The height of the machine in chips;
            this parameter is deprecated
        :param dict(SystemVariableDefinition,object) extra_boot_values:
            Any additional values to set during boot
        :return: version info
        :rtype: VersionInfo
        :raise SpinnmanIOException:
            If there is a problem communicating with the machine
        """
        version_info = None
        current_tries_to_go = tries_to_go
        while version_info is None and current_tries_to_go > 0:
            try:
                version_info = self.get_scamp_version(n_retries=BOOT_RETRIES)
                if self.__is_default_destination(version_info):
                    version_info = None
                    time.sleep(0.1)
            except SpinnmanGenericProcessException as e:
                if isinstance(e.exception, SpinnmanTimeoutException):
                    logger.info("Attempting to boot machine")
                    self.boot_board(
                        number_of_boards, width, height, extra_boot_values)
                    current_tries_to_go -= 1
                elif isinstance(e.exception, SpinnmanIOException):
                    raise SpinnmanIOException(
                        "Failed to communicate with the machine") from e
                else:
                    raise
            except SpinnmanTimeoutException:
                logger.info("Attempting to boot machine")
                self.boot_board(
                    number_of_boards, width, height, extra_boot_values)
                current_tries_to_go -= 1
            except SpinnmanIOException as e:
                raise SpinnmanIOException(
                    "Failed to communicate with the machine") from e

        # The last thing we tried was booting, so try again to get the version
        if version_info is None:
            try:
                version_info = self.get_scamp_version()
                if self.__is_default_destination(version_info):
                    version_info = None
            except SpinnmanException:
                pass
        if version_info is not None:
            logger.info("Found board with version {}", version_info)
        return version_info

    def get_cpu_information(self, core_subsets=None):
        """ Get information about the processors on the board

        :param ~spinn_machine.CoreSubsets core_subsets:
            A set of chips and cores from which to get the
            information. If not specified, the information from all of the
            cores on all of the chips on the board are obtained.
        :return: An iterable of the CPU information for the selected cores, or
            all cores if core_subsets is not specified
        :rtype: list(CPUInfo)
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
            if self._machine is None:
                self._update_machine()
            core_subsets = CoreSubsets()
            for chip in self._machine.chips:
                for processor in chip.processors:
                    core_subsets.add_processor(
                        chip.x, chip.y, processor.processor_id)

        process = GetCPUInfoProcess(self._scamp_connection_selector)
        cpu_info = process.get_cpu_info(core_subsets)
        return cpu_info

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
    def get_user_0_register_address_from_core(p):
        """ Get the address of user 0 for a given processor on the board

        :param int p: The ID of the processor to get the user 0 address from
        :return: The address for user 0 register for this processor
        :rtype: int
        """
        return get_vcpu_address(p) + CPU_USER_0_START_ADDRESS

    def read_user_0(self, x, y, p):
        """ Get the contents of the user_0 register for the given processor.

        :param int x: X coordinate of the chip
        :param int y: Y coordinate of the chip
        :param int p: Virtual processor identifier on the chip
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
        addr = self.get_user_0_register_address_from_core(p)
        return struct.unpack("<I", self.read_memory(x, y, addr, 4))[0]

    def read_user_1(self, x, y, p):
        """ Get the contents of the user_1 register for the given processor.

        :param int x: X coordinate of the chip
        :param int y: Y coordinate of the chip
        :param int p: Virtual processor identifier on the chip
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
        addr = self.get_user_1_register_address_from_core(p)
        return struct.unpack("<I", self.read_memory(x, y, addr, 4))[0]

    @staticmethod
    def get_user_1_register_address_from_core(p):
        """ Get the address of user 1 for a given processor on the board

        :param int p: The ID of the processor to get the user 1 address from
        :return: The address for user 1 register for this processor
        :rtype: int
        """
        return get_vcpu_address(p) + CPU_USER_1_START_ADDRESS

    @staticmethod
    def get_user_2_register_address_from_core(p):
        """ Get the address of user 2 for a given processor on the board

        :param int p: The ID of the processor to get the user 2 address from
        :return: The address for user 2 register for this processor
        :rtype: int
        """
        return get_vcpu_address(p) + CPU_USER_2_START_ADDRESS

    @staticmethod
    def get_user_3_register_address_from_core(p):
        """ Get the address of user 3 for a given processor on the board

        :param int p: The ID of the processor to get the user 3 address from
        :return: The address for user 3 register for this processor
        :rtype: int
        """
        return get_vcpu_address(p) + CPU_USER_3_START_ADDRESS

    def get_cpu_information_from_core(self, x, y, p):
        """ Get information about a specific processor on the board

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
        return next(iter(self.get_cpu_information(core_subsets)))

    def get_iobuf(self, core_subsets=None):
        """ Get the contents of the IOBUF buffer for a number of processors

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

    def set_watch_dog_on_chip(self, x, y, watch_dog):
        """ Enable, disable or set the value of the watch dog timer on a\
            specific chip

        :param int x: chip x coord to write new watchdog param to
        :param int y: chip y coord to write new watchdog param to
        :param watch_dog:
            Either a boolean indicating whether to enable (True) or
            disable (False) the watchdog timer, or an int value to set the
            timer count to
        :type watch_dog: bool or int
        """
        # build what we expect it to be
        value_to_set = watch_dog
        WATCHDOG = SystemVariableDefinition.software_watchdog_count
        if isinstance(watch_dog, bool):
            value_to_set = WATCHDOG.default if watch_dog else 0

        # build data holder
        data = _ONE_BYTE.pack(value_to_set)

        # write data
        address = SYSTEM_VARIABLE_BASE_ADDRESS + WATCHDOG.offset
        self.write_memory(x=x, y=y, base_address=address, data=data)

    def set_watch_dog(self, watch_dog):
        """ Enable, disable or set the value of the watch dog timer

        :param watch_dog:
            Either a boolean indicating whether to enable (True) or
            disable (False) the watch dog timer, or an int value to set the
            timer count to.
        :type watch_dog: bool or int
        """
        if self._machine is None:
            self._update_machine()
        for x, y in self._machine.chip_coordinates:
            self.set_watch_dog_on_chip(x, y, watch_dog)

    def get_iobuf_from_core(self, x, y, p):
        """ Get the contents of IOBUF for a given core

        :param int x: The x-coordinate of the chip containing the processor
        :param int y: The y-coordinate of the chip containing the processor
        :param int p: The ID of the processor to get the IOBUF for
        :return: An IOBUF buffer
        :rtype: IOBuffer
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
        core_subsets = CoreSubsets()
        core_subsets.add_processor(x, y, p)
        return next(self.get_iobuf(core_subsets))

    def get_core_state_count(self, app_id, state):
        """ Get a count of the number of cores which have a given state

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

    def execute(
            self, x, y, processors, executable, app_id, n_bytes=None,
            wait=False, is_filename=False):
        """ Start an executable running on a single chip

        :param int x:
            The x-coordinate of the chip on which to run the executable
        :param int y:
            The y-coordinate of the chip on which to run the executable
        :param list(int) processors:
            The cores on the chip on which to run the application
        :param executable:
            The data that is to be executed. Should be one of the following:

            * An instance of RawIOBase
            * A bytearray/bytes
            * A filename of a file containing the executable (in which case\
              `is_filename` must be set to True)
        :type executable:
            ~io.RawIOBase or bytes or bytearray or str
        :param int app_id:
            The ID of the application with which to associate the executable
        :param int n_bytes:
            The size of the executable data in bytes. If not specified:

            * If executable is an RawIOBase, an error is raised
            * If executable is a bytearray, the length of the bytearray will\
              be used
            * If executable is an int, 4 will be used
            * If executable is a str, the length of the file will be used
        :param bool wait:
            True if the binary should enter a "wait" state on loading
        :param bool is_filename: True if executable is a filename
        :raise SpinnmanIOException:
            * If there is an error communicating with the board
            * If there is an error reading the executable
        :raise SpinnmanInvalidPacketException:
            If a packet is received that is not in the valid format
        :raise SpinnmanInvalidParameterException:
            * If x, y, p does not lead to a valid core
            * If app_id is an invalid application ID
            * If a packet is received that has invalid parameters
        :raise SpinnmanUnexpectedResponseCodeException:
            If a response indicates an error during the exchange
        """

        # Lock against updates
        self._get_chip_execute_lock(x, y)

        # Write the executable
        EXECUTABLE_ADDRESS = 0x67800000
        self.write_memory(
            x, y, EXECUTABLE_ADDRESS, executable, n_bytes,
            is_filename=is_filename)

        # Request the start of the executable
        process = SendSingleCommandProcess(self._scamp_connection_selector)
        process.execute(ApplicationRun(app_id, x, y, processors, wait))

        # Release the lock
        self._release_chip_execute_lock(x, y)

    def _get_next_nearest_neighbour_id(self):
        with self._nearest_neighbour_lock:
            next_nearest_neighbour_id = (self._nearest_neighbour_id + 1) % 127
            self._nearest_neighbour_id = next_nearest_neighbour_id
        return next_nearest_neighbour_id

    def execute_flood(
            self, core_subsets, executable, app_id, n_bytes=None, wait=False,
            is_filename=False):
        """ Start an executable running on multiple places on the board.  This\
            will be optimised based on the selected cores, but it may still\
            require a number of communications with the board to execute.

        :param ~spinn_machine.CoreSubsets core_subsets:
            Which cores on which chips to start the executable
        :param executable:
            The data that is to be executed. Should be one of the following:

            * An instance of RawIOBase
            * A bytearray
            * A filename of an executable (in which case `is_filename` must be\
              set to True)
        :type executable:
            ~io.RawIOBase or bytes or bytearray or str
        :param int app_id:
            The ID of the application with which to associate the executable
        :param int n_bytes:
            The size of the executable data in bytes. If not specified:

            * If `executable` is an RawIOBase, an error is raised
            * If `executable` is a bytearray, the length of the bytearray will\
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
        self._get_flood_execute_lock()

        # Flood fill the system with the binary
        self.write_memory_flood(
            0x67800000, executable, n_bytes, is_filename=is_filename)

        # Execute the binary on the cores on the chips where required
        process = ApplicationRunProcess(self._scamp_connection_selector)
        process.run(app_id, core_subsets, wait)

        # Release the lock
        self._release_flood_execute_lock()

    def execute_application(self, executable_targets, app_id):
        """ Execute a set of binaries that make up a complete application\
            on specified cores, wait for them to be ready and then start\
            all of the binaries.  Note this will get the binaries into c_main\
            but will not signal the barrier.

        :param ExecutableTargets executable_targets:
            The binaries to be executed and the cores to execute them on
        :param int app_id: The app_id to give this application
        """
        # Execute each of the binaries and get them in to a "wait" state
        for binary in executable_targets.binaries:
            core_subsets = executable_targets.get_cores_for_binary(binary)
            self.execute_flood(
                core_subsets, binary, app_id, wait=True, is_filename=True)

        # Sleep to allow cores to get going
        time.sleep(0.5)

        # Check that the binaries have reached a wait state
        count = self.get_core_state_count(app_id, CPUState.READY)
        if count < executable_targets.total_processors:
            cores_ready = self.get_cores_not_in_state(
                executable_targets.all_core_subsets, [CPUState.READY])
            if len(cores_ready) > 0:
                raise SpinnmanException(
                    "Only {} of {} cores reached ready state: {}".format(
                        count, executable_targets.total_processors,
                        self.get_core_status_string(cores_ready)))

        # Send a signal telling the application to start
        self.send_signal(app_id, Signal.START)

    def power_on_machine(self):
        """ Power on the whole machine
        :rtype bool
        :return success of failure to power on machine
        """
        if not self._bmp_connections:
            logger.warning("No BMP connections, so can't power on")
            return False
        for bmp_connection in self._bmp_connections:
            self.power_on(bmp_connection.boards, bmp_connection.cabinet,
                          bmp_connection.frame)
        return True

    def power_on(self, boards=0, cabinet=0, frame=0):
        """ Power on a set of boards in the machine

        :param int boards: The board or boards to power on
        :param int cabinet: the ID of the cabinet containing the frame, or 0
            if the frame is not in a cabinet
        :param int frame: the ID of the frame in the cabinet containing the
            board(s), or 0 if the board is not in a frame
        """
        self._power(PowerCommand.POWER_ON, boards, cabinet, frame)

    def power_off_machine(self):
        """ Power off the whole machine
        :rtype bool
        :return success or failure to power off the machine
        """
        if not self._bmp_connections:
            logger.warning("No BMP connections, so can't power off")
            return False
        for bmp_connection in self._bmp_connections:
            self.power_off(bmp_connection.boards, bmp_connection.cabinet,
                           bmp_connection.frame)
        return True

    def power_off(self, boards=0, cabinet=0, frame=0):
        """ Power off a set of boards in the machine

        :param int boards: The board or boards to power off
        :param int cabinet: the ID of the cabinet containing the frame, or 0
            if the frame is not in a cabinet
        :param int frame: the ID of the frame in the cabinet containing the
            board(s), or 0 if the board is not in a frame
        """
        self._power(PowerCommand.POWER_OFF, boards, cabinet, frame)

    def _bmp_connection(self, cabinet, frame):
        """
        :param int cabinet:
        :param int frame:
        :rtype: MostDirectConnectionSelector
        """
        key = (cabinet, frame)
        if key not in self._bmp_connection_selectors:
            raise SpinnmanInvalidParameterException(
                "cabinet and frame", "{} and {}".format(cabinet, frame),
                "Unknown combination")
        return self._bmp_connection_selectors[key]

    def _power(self, power_command, boards=0, cabinet=0, frame=0):
        """ Send a power request to the machine

        :param PowerCommand power_command: The power command to send
        :param boards: The board or boards to send the command to
        :param int cabinet: the ID of the cabinet containing the frame, or 0
            if the frame is not in a cabinet
        :param int frame: the ID of the frame in the cabinet containing the
            board(s), or 0 if the board is not in a frame
        """
        connection_selector = self._bmp_connection(cabinet, frame)
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

    def set_led(self, led, action, board, cabinet, frame):
        """ Set the LED state of a board in the machine

        :param led:
            Number of the LED or an iterable of LEDs to set the state of (0-7)
        :type led: int or iterable(int)
        :param LEDAction action:
            State to set the LED to, either on, off or toggle
        :param board: Specifies the board to control the LEDs of. This may
            also be an iterable of multiple boards (in the same frame). The
            command will actually be sent to the first board in the iterable.
        :type board: int or iterable(int)
        :param int cabinet: the cabinet this is targeting
        :param int frame: the frame this is targeting
        """
        process = SendSingleCommandProcess(
            self._bmp_connection(cabinet, frame))
        process.execute(BMPSetLed(led, action, board))

    def read_fpga_register(self, fpga_num, register, cabinet, frame, board):
        """ Read a register on a FPGA of a board. The meaning of the\
            register's contents will depend on the FPGA's configuration.

        :param int fpga_num: FPGA number (0, 1 or 2) to communicate with.
        :param int register:
            Register address to read to (will be rounded down to
            the nearest 32-bit word boundary).
        :param int cabinet: cabinet: the cabinet this is targeting
        :param int frame: the frame this is targeting
        :param int board: which board to request the FPGA register from
        :return: the register data
        :rtype: int
        """
        process = SendSingleCommandProcess(
            self._bmp_connection(cabinet, frame), timeout=1.0)
        response = process.execute(
            ReadFPGARegister(fpga_num, register, board))
        return response.fpga_register  # pylint: disable=no-member

    def write_fpga_register(self, fpga_num, register, value, cabinet, frame,
                            board):
        """ Write a register on a FPGA of a board. The meaning of setting the\
            register's contents will depend on the FPGA's configuration.

        :param int fpga_num: FPGA number (0, 1 or 2) to communicate with.
        :param int register:
            Register address to read to (will be rounded down to
            the nearest 32-bit word boundary).
        :param int value: the value to write into the FPGA register
        :param int cabinet: cabinet: the cabinet this is targeting
        :param int frame: the frame this is targeting
        :param int board: which board to write the FPGA register to
        """
        process = SendSingleCommandProcess(
            self._bmp_connection(cabinet, frame))
        process.execute(
            WriteFPGARegister(fpga_num, register, value, board))

    def read_adc_data(self, board, cabinet, frame):
        """ Read the BMP ADC data

        :param int cabinet: cabinet: the cabinet this is targeting
        :param int frame: the frame this is targeting
        :param int board: which board to request the ADC data from
        :return: the FPGA's ADC data object
        :rtype: ADCInfo
        """
        process = SendSingleCommandProcess(
            self._bmp_connection(cabinet, frame))
        response = process.execute(ReadADC(board))
        return response.adc_info  # pylint: disable=no-member

    def read_bmp_version(self, board, cabinet, frame):
        """ Read the BMP version

        :param int cabinet: cabinet: the cabinet this is targeting
        :param int frame: the frame this is targeting
        :param int board: which board to request the data from
        :return: the sver from the BMP
        """
        process = SendSingleCommandProcess(
            self._bmp_connection(cabinet, frame))
        response = process.execute(BMPGetVersion(board))
        return response.version_info  # pylint: disable=no-member

    def write_memory(self, x, y, base_address, data, n_bytes=None, offset=0,
                     cpu=0, is_filename=False):
        """ Write to the SDRAM on the board.

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
            * A filename of a data file (in which case `is_filename` must be\
              set to True)
        :type data:
            ~io.RawIOBase or bytes or bytearray or int or str
        :param int n_bytes:
            The amount of data to be written in bytes.  If not specified:

            * If `data` is an RawIOBase, an error is raised
            * If `data` is a bytearray, the length of the bytearray will be\
              used
            * If `data` is an int, 4 will be used
            * If `data` is a str, the length of the file will be used
        :param int offset: The offset from which the valid data begins
        :param int cpu: The optional CPU to write to
        :param bool is_filename: True if `data` is a filename
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
            process.write_memory_from_reader(
                x, y, cpu, base_address, data, n_bytes)
        elif isinstance(data, str) and is_filename:
            if n_bytes is None:
                n_bytes = os.stat(data).st_size
            with open(data, "rb") as reader:
                process.write_memory_from_reader(
                    x, y, cpu, base_address, reader, n_bytes)
        elif isinstance(data, int):
            data_to_write = _ONE_WORD.pack(data)
            process.write_memory_from_bytearray(
                x, y, cpu, base_address, data_to_write, 0, 4)
        else:
            if n_bytes is None:
                n_bytes = len(data)
            process.write_memory_from_bytearray(
                x, y, cpu, base_address, data, offset, n_bytes)

    def write_neighbour_memory(self, x, y, link, base_address, data,
                               n_bytes=None, offset=0, cpu=0):
        """ Write to the memory of a neighbouring chip using a LINK_READ SCP\
            command. If sent to a BMP, this command can be used to communicate\
            with the FPGAs' debug registers.

        :param int x:
            The x-coordinate of the chip whose neighbour is to be written to
        :param int y:
            The y-coordinate of the chip whose neighbour is to be written to
        :param int link:
            The link index to send the request to (or if BMP, the FPGA number)
        :param int base_address:
            The address in SDRAM where the region of memory is to be written
        :param data: The data to write.  Should be one of the following:

            * An instance of RawIOBase
            * A bytearray/bytes
            * A single integer; will be written in little-endian byte order
        :type data:
            ~io.RawIOBase or bytes or bytearray or int
        :param int n_bytes:
            The amount of data to be written in bytes.  If not specified:

            * If `data` is an RawIOBase, an error is raised
            * If `data` is a bytearray, the length of the bytearray will be\
              used
            * If `data` is an int, 4 will be used
        :param int offset:
            The offset where the valid data starts (if `data` is
            an int then offset will be ignored and used 0)
        :param int cpu:
            The CPU to use, typically 0 (or if a BMP, the slot number)
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
            process.write_link_memory_from_reader(
                x, y, cpu, link, base_address, data, n_bytes)
        elif isinstance(data, int):
            data_to_write = _ONE_WORD.pack(data)
            process.write_link_memory_from_bytearray(
                x, y, cpu, link, base_address, data_to_write, 0, 4)
        else:
            if n_bytes is None:
                n_bytes = len(data)
            process.write_link_memory_from_bytearray(
                x, y, cpu, link, base_address, data, offset, n_bytes)

    def write_memory_flood(
            self, base_address, data, n_bytes=None, offset=0,
            is_filename=False):
        """ Write to the SDRAM of all chips.

        :param int base_address:
            The address in SDRAM where the region of memory is to be written
        :param data:
            The data that is to be written.  Should be one of the following:

            * An instance of RawIOBase
            * A bytearray or bytestring
            * A single integer
            * A file name of a file to read (in which case `is_filename`\
              should be set to True)
        :type data:
            ~io.RawIOBase or bytes or bytearray or int or str
        :param int n_bytes:
            The amount of data to be written in bytes.  If not specified:

            * If `data` is an RawIOBase, an error is raised
            * If `data` is a bytearray, the length of the bytearray will be\
              used
            * If `data` is an int, 4 will be used
            * If `data` is a str, the size of the file will be used
        :param int offset:
            The offset where the valid data starts; if `data` is
            an int, then the offset will be ignored and 0 is used.
        :param bool is_filename:
            True if `data` should be interpreted as a file name
        :raise SpinnmanIOException:
            * If there is an error communicating with the board
            * If there is an error reading the executable
        :raise SpinnmanInvalidPacketException:
            If a packet is received that is not in the valid format
        :raise SpinnmanInvalidParameterException:
            * If one of the specified chips is not valid
            * If `app_id` is an invalid application ID
            * If a packet is received that has invalid parameters
        :raise SpinnmanUnexpectedResponseCodeException:
            If a response indicates an error during the exchange
        """
        process = WriteMemoryFloodProcess(self._scamp_connection_selector)
        # Ensure only one flood fill occurs at any one time
        with self._flood_write_lock:
            # Start the flood fill
            nearest_neighbour_id = self._get_next_nearest_neighbour_id()
            if isinstance(data, io.RawIOBase):
                process.write_memory_from_reader(
                    nearest_neighbour_id, base_address, data, n_bytes)
            elif isinstance(data, str) and is_filename:
                if n_bytes is None:
                    n_bytes = os.stat(data).st_size
                with open(data, "rb") as reader:
                    process.write_memory_from_reader(
                        nearest_neighbour_id, base_address, reader, n_bytes)
            elif isinstance(data, int):
                data_to_write = _ONE_WORD.pack(data)
                process.write_memory_from_bytearray(
                    nearest_neighbour_id, base_address, data_to_write, 0)
            else:
                if n_bytes is None:
                    n_bytes = len(data)
                process.write_memory_from_bytearray(
                    nearest_neighbour_id, base_address, data, offset, n_bytes)

    def read_memory(self, x, y, base_address, length, cpu=0):
        """ Read some areas of memory (usually SDRAM) from the board.

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

        process = ReadMemoryProcess(self._scamp_connection_selector)
        return process.read_memory(x, y, cpu, base_address, length)

    def read_word(self, x, y, base_address, cpu=0):
        """ Read a word (usually of SDRAM) from the board.

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
        process = ReadMemoryProcess(self._scamp_connection_selector)
        data = process.read_memory(x, y, cpu, base_address, _ONE_WORD.size)
        (value, ) = _ONE_WORD.unpack(data)
        return value

    def read_neighbour_memory(self, x, y, link, base_address, length, cpu=0):
        """ Read some areas of memory on a neighbouring chip using a LINK_READ\
            SCP command. If sent to a BMP, this command can be used to\
            communicate with the FPGAs' debug registers.

        :param int x:
            The x-coordinate of the chip whose neighbour is to be read from
        :param int y:
            The y-coordinate of the chip whose neighbour is to be read from
        :param int cpu:
            The CPU to use, typically 0 (or if a BMP, the slot number)
        :param int link:
            The link index to send the request to (or if BMP, the FPGA number)
        :param int base_address:
            The address in SDRAM where the region of memory to be read starts
        :param int length: The length of the data to be read in bytes
        :return: An iterable of chunks of data read in order
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

        process = ReadMemoryProcess(self._scamp_connection_selector)
        return process.read_link_memory(x, y, cpu, link, base_address, length)

    def stop_application(self, app_id):
        """ Sends a stop request for an app_id

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

    def wait_for_cores_to_be_in_state(
            self, all_core_subsets, app_id, cpu_states, timeout=None,
            time_between_polls=0.1,
            error_states=frozenset({
                CPUState.RUN_TIME_EXCEPTION, CPUState.WATCHDOG}),
            counts_between_full_check=100, progress_bar=None):
        """ Waits for the specified cores running the given application to be\
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
                    error_core_states = self.get_cores_in_state(
                        all_core_subsets, error_states)
                    if len(error_core_states) > 0:
                        raise SpiNNManCoresNotInStateException(
                            timeout, cpu_states, error_core_states)

                # If we haven't seen an error, increase the tries, and
                # do a full check if required
                tries += 1
                if tries >= counts_between_full_check:
                    cores_in_state = self.get_cores_in_state(
                        all_core_subsets, cpu_states)
                    processors_ready = len(cores_in_state)
                    tries = 0

                    # iterate over the cores waiting to finish and see
                    # which ones we're missing
                    if self._report_waiting_logs:
                        for core_subset in all_core_subsets.core_subsets:
                            for p in core_subset.processor_ids:
                                if ((core_subset.x, core_subset.y, p) not in
                                        cores_in_state.keys()):
                                    logger.warning(
                                        "waiting on {}:{}:{}".format(
                                            core_subset.x, core_subset.y, p))

                # If we're still not in the correct state, wait a bit
                if processors_ready < len(all_core_subsets):
                    time.sleep(time_between_polls)

        # If we haven't reached the final state, do a final full check
        if processors_ready < len(all_core_subsets):
            cores_not_in_state = self.get_cores_not_in_state(
                all_core_subsets, cpu_states)

            # If we are sure we haven't reached the final state,
            # report a timeout error
            if len(cores_not_in_state) != 0:
                raise SpiNNManCoresNotInStateException(
                    timeout, cpu_states, cores_not_in_state)

    def get_cores_in_state(self, all_core_subsets, states):
        """ Get all cores that are in a given state or set of states

        :param ~spinn_machine.CoreSubsets all_core_subsets:
            The cores to filter
        :param states: The state or states to filter on
        :type states: CPUState or set(CPUState)
        :return: Core subsets object containing cores in the given state(s)
        :rtype: CPUInfos
        """
        core_infos = self.get_cpu_information(all_core_subsets)
        cores_in_state = CPUInfos()
        for core_info in core_infos:
            if hasattr(states, "__iter__"):
                if core_info.state in states:
                    cores_in_state.add_processor(
                        core_info.x, core_info.y, core_info.p, core_info)
            elif core_info.state == states:
                cores_in_state.add_processor(
                    core_info.x, core_info.y, core_info.p, core_info)

        return cores_in_state

    def get_cores_not_in_state(self, all_core_subsets, states):
        """ Get all cores that are not in a given state or set of states

        :param ~spinn_machine.CoreSubsets all_core_subsets:
            The cores to filter
        :param states: The state or states to filter on
        :type states: CPUState or set(CPUState)
        :return: Core subsets object containing cores not in the given state(s)
        :rtype: ~spinn_machine.CoreSubsets
        """
        core_infos = self.get_cpu_information(all_core_subsets)
        cores_not_in_state = CPUInfos()
        for core_info in core_infos:
            if hasattr(states, "__iter__"):
                if core_info.state not in states:
                    cores_not_in_state.add_processor(
                        core_info.x, core_info.y, core_info.p, core_info)
            elif core_info.state != states:
                cores_not_in_state.add_processor(
                    core_info.x, core_info.y, core_info.p, core_info)
        return cores_not_in_state

    def get_core_status_string(self, cpu_infos):
        """ Get a string indicating the status of the given cores

        :param CPUInfos cpu_infos: A CPUInfos objects
        :rtype: str
        """
        break_down = "\n"
        for (x, y, p), core_info in cpu_infos.cpu_infos:
            if core_info.state == CPUState.RUN_TIME_EXCEPTION:
                break_down += "    {}:{}:{} in state {}:{}\n".format(
                    x, y, p, core_info.state.name,
                    core_info.run_time_error.name)
                break_down += "        r0={}, r1={}, r2={}, r3={}\n".format(
                    core_info.registers[0], core_info.registers[1],
                    core_info.registers[2], core_info.registers[3])
                break_down += "        r4={}, r5={}, r6={}, r7={}\n".format(
                    core_info.registers[4], core_info.registers[5],
                    core_info.registers[6], core_info.registers[7])
                break_down += "        PSR={}, SP={}, LR={}".format(
                    core_info.processor_state_register,
                    core_info.stack_pointer, core_info.link_register)
            else:
                break_down += "    {}:{}:{} in state {}\n".format(
                    x, y, p, core_info.state.name)
        return break_down

    def send_signal(self, app_id, signal):
        """ Send a signal to an application

        :param int app_id: The ID of the application to send to
        :param Signal signal: The signal to send
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

    def set_leds(self, x, y, cpu, led_states):
        """ Set SetLED states.

        :param int x: The x-coordinate of the chip on which to set the LEDs
        :param int y: The x-coordinate of the chip on which to set the LEDs
        :param int cpu: The CPU of the chip on which to set the LEDs
        :param dict(int,int) led_states:
            A dictionary mapping SetLED index to state with
            0 being off, 1 on and 2 inverted.
        :raise SpinnmanIOException:
            If there is an error communicating with the board
        :raise SpinnmanInvalidPacketException:
            If a packet is received that is not in the valid format
        :raise SpinnmanInvalidParameterException:
            If a packet is received that has invalid parameters
        :raise SpinnmanUnexpectedResponseCodeException:
            If a response indicates an error during the exchange
        """
        process = SendSingleCommandProcess(self._scamp_connection_selector)
        process.execute(SetLED(x, y, cpu, led_states))

    def locate_spinnaker_connection_for_board_address(self, board_address):
        """ Find a connection that matches the given board IP address

        :param str board_address:
            The IP address of the Ethernet connection on the board
        :return: A connection for the given IP address, or None if no such
            connection exists
        :rtype: SCAMPConnection
        """
        return self._udp_scamp_connections.get(board_address, None)

    def set_ip_tag(self, ip_tag, use_sender=False):
        """ Set up an IP tag

        :param ~spinn_machine.tags.IPTag ip_tag:
            The tag to set up; note `board_address` can be None, in
            which case, the tag will be assigned to all boards
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
        """ Get the connections for talking to a board.

        :param SCPSender connection:
            Optional param that directly gives the connection to use.
        :param str board_address:
            Optional param that gives the address of the board to talk to.
        :return: List of length 1 or 0 (the latter only if the search for
            the given board address fails).
        :rtype: list(SCPSender)
        """
        if connection is not None:
            return [connection]
        elif board_address is None:
            return self._scamp_connections

        connection = self.locate_spinnaker_connection_for_board_address(
            board_address)
        if connection is None:
            return []
        return [connection]

    def set_reverse_ip_tag(self, reverse_ip_tag):
        """ Set up a reverse IP tag

        :param ~spinn_machine.tags.ReverseIPTag reverse_ip_tag:
            The reverse tag to set up; note `board_address` can be None,
            in which case, the tag will be assigned to all boards
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
                " the SpiNNaker system ports ({} and {})".format(
                    SCP_SCAMP_PORT, UDP_BOOT_CONNECTION_DEFAULT_PORT))

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
        """ Clear the setting of an IP tag

        :param int tag: The tag ID
        :param str board_address:
            Board address where the tag should be cleared.
            If not specified, all SCPSender connections will send the message
            to clear the tag
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
        """ Get the current set of tags that have been set on the board

        :param SCPSender connection:
            Connection from which the tags should be received.
            If not specified, all SCPSender connections will be queried and
            the response will be combined.
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
        """ Allocates a chunk of SDRAM on a chip on the machine

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
        process = MallocSDRAMProcess(self._scamp_connection_selector)
        process.malloc_sdram(x, y, size, app_id, tag)
        return process.base_address

    def free_sdram(self, x, y, base_address, app_id):
        """ Free allocated SDRAM

        :param int x: The x-coordinate of the chip onto which to ask for memory
        :param int y: The y-coordinate of the chip onto which to ask for memory
        :param int base_address: The base address of the allocated memory
        :param int app_id: The app ID of the allocated memory
        """
        process = DeAllocSDRAMProcess(self._scamp_connection_selector)
        process.de_alloc_sdram(x, y, app_id, base_address)

    def free_sdram_by_app_id(self, x, y, app_id):
        """ Free all SDRAM allocated to a given app ID

        :param int x: The x-coordinate of the chip onto which to ask for memory
        :param int y: The y-coordinate of the chip onto which to ask for memory
        :param int app_id: The app ID of the allocated memory
        :return: The number of blocks freed
        :rtype: int
        """
        process = DeAllocSDRAMProcess(self._scamp_connection_selector)
        process.de_alloc_sdram(x, y, app_id)
        return process.no_blocks_freed

    def load_multicast_routes(self, x, y, routes, app_id):
        """ Load a set of multicast routes on to a chip

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

        process = LoadMultiCastRoutesProcess(self._scamp_connection_selector)
        process.load_routes(x, y, routes, app_id)

    def load_fixed_route(self, x, y, fixed_route, app_id):
        """ Loads a fixed route routing table entry onto a chip's router.

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
        process = LoadFixedRouteRoutingEntryProcess(
            self._scamp_connection_selector)
        process.load_fixed_route(x, y, fixed_route, app_id)

    def read_fixed_route(self, x, y, app_id):
        """ Reads a fixed route routing table entry from a chip's router.

        :param int x:
            The x-coordinate of the chip onto which to load the routes
        :param int y:
            The y-coordinate of the chip onto which to load the routes
        :param int app_id:
            The ID of the application with which to associate the
            routes.  If not specified, defaults to 0.
        :return: the route as a fixed route entry
        """
        process = ReadFixedRouteRoutingEntryProcess(
            self._scamp_connection_selector)
        return process.read_fixed_route(x, y, app_id)

    def get_multicast_routes(self, x, y, app_id=None):
        """ Get the current multicast routes set up on a chip

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
        base_address = self._get_sv_data(
            x, y, SystemVariableDefinition.router_table_copy_address)
        process = GetMultiCastRoutesProcess(
            self._scamp_connection_selector, app_id)
        return process.get_routes(x, y, base_address)

    def clear_multicast_routes(self, x, y):
        """ Remove all the multicast routes on a chip

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
        process = SendSingleCommandProcess(self._scamp_connection_selector)
        process.execute(RouterClear(x, y))

    def get_router_diagnostics(self, x, y):
        """ Get router diagnostic information from a chip

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
        process = ReadRouterDiagnosticsProcess(self._scamp_connection_selector)
        return process.get_router_diagnostics(x, y)

    def set_router_diagnostic_filter(self, x, y, position, diagnostic_filter):
        """ Sets a router diagnostic filter in a router

        :param int x:
            the X address of the router in which this filter is being set
        :param int y:
            the Y address of the router in which this filter is being set
        :param int position:
            the position in the list of filters where this filter is to be
            added
        :param DiagnosticFilter diagnostic_filter:
            the diagnostic filter being set in the placed, between 0 and 15
            (note that positions 0 to 11 are used by the default filters,
            and setting these positions will result in a warning).
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

    def get_router_diagnostic_filter(self, x, y, position):
        """ Gets a router diagnostic filter from a router

        :param int x:
            the X address of the router from which this filter is being
            retrieved
        :param int y:
            the Y address of the router from which this filter is being
            retrieved
        :param int position:
            the position in the list of filters to read the information from
        :return: The diagnostic filter read
        :rtype: DiagnosticFilter
        :raise SpinnmanIOException:
            * If there is an error communicating with the board
            * If there is an error reading the data
        :raise SpinnmanInvalidPacketException:
            If a packet is received that is not in the valid format
        :raise SpinnmanInvalidParameterException:
            * If x, y does not lead to a valid chip
            * If a packet is received that has invalid parameters
            * If position is less than 0 or more than 15
        :raise SpinnmanUnexpectedResponseCodeException:
            If a response indicates an error during the exchange
        """
        memory_position = (
            ROUTER_REGISTER_BASE_ADDRESS + ROUTER_FILTER_CONTROLS_OFFSET +
            position * ROUTER_DIAGNOSTIC_FILTER_SIZE)

        process = SendSingleCommandProcess(self._scamp_connection_selector)
        response = process.execute(ReadMemory(x, y, memory_position, 4))
        return DiagnosticFilter.read_from_int(_ONE_WORD.unpack_from(
            response.data, response.offset)[0])  # pylint: disable=no-member

    def clear_router_diagnostic_counters(self, x, y, enable=True,
                                         counter_ids=None):
        """ Clear router diagnostic information on a chip

        :param int x: The x-coordinate of the chip
        :param int y: The y-coordinate of the chip
        :param bool enable: True (default) if the counters should be enabled
        :param iterable(int) counter_ids:
            The IDs of the counters to reset (all by default)\
            and enable if enable is True; each must be between 0 and 15
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
        if counter_ids is None:
            counter_ids = range(0, 16)
        clear_data = 0
        for counter_id in counter_ids:
            if counter_id < 0 or counter_id > 15:
                raise SpinnmanInvalidParameterException(
                    "counter_id", counter_id,
                    "Diagnostic counter IDs must be between 0 and 15")
            clear_data |= 1 << counter_id
        if enable:
            for counter_id in counter_ids:
                clear_data |= 1 << counter_id + 16
        process = SendSingleCommandProcess(self._scamp_connection_selector)
        process.execute(WriteMemory(
            x, y, 0xf100002c, _ONE_WORD.pack(clear_data)))

    @property
    def number_of_boards_located(self):
        """ The number of boards currently configured.

        :rtype: int
        """
        boards = 0
        for bmp_connection in self._bmp_connections:
            boards += len(bmp_connection.boards)

        # if no BMPs are available, then there's still at least one board
        return max(1, boards)

    def close(self, close_original_connections=True, power_off_machine=False):
        """ Close the transceiver and any threads that are running

        :param bool close_original_connections:
            If True, the original connections passed to the transceiver in the
            constructor are also closed.
            If False, only newly discovered connections are closed.
        :param bool power_off_machine:
            if True, the machine is sent a power down
            command via its BMP (if it has one)
        """
        # pylint: disable=arguments-differ
        if power_off_machine and self._bmp_connections:
            self.power_off_machine()

        for connections in self._udp_receive_connections_by_port.values():
            for (_, listener) in connections.values():
                if listener is not None:
                    listener.close()

        for connection in self._all_connections:
            if (close_original_connections or
                    connection not in self._original_connections):
                connection.close()

    def register_udp_listener(self, callback, connection_class,
                              local_port=None, local_host=None):
        """ Register a callback for a certain type of traffic to be received\
            via UDP. Note that the connection class must extend\
            :py:class:`Listenable` to avoid clashing with the SCAMP and BMP\
            functionality.

        :param callable callback:
            Function to be called when a packet is received
        :param type connection_class:
            The class of connection to receive using (a subclass of
            :py:class:`Listenable`)
        :param int local_port: The optional port number to listen on; if not
            specified, an existing connection will be used if possible,
            otherwise a random free port number will be used
        :param str local_host: The optional hostname or IP address to listen
            on; if not specified, all interfaces will be used for listening
        :return: The connection to be used
        :rtype: UDPConnection
        """

        # If the connection class is not an Listenable, this is an
        # error
        if not issubclass(connection_class, Listenable):
            raise SpinnmanInvalidParameterException(
                "connection_class", connection_class,
                "The connection class must be Listenable")

        connections_of_class = self._udp_listenable_connections_by_class[
            connection_class]
        connection = None
        listener = None

        # If the local port was specified
        if local_port is not None:
            receiving_connections = self._udp_receive_connections_by_port[
                local_port]

            # If something is already listening on this port
            if receiving_connections:

                if local_host is None or local_host == "0.0.0.0":
                    # If we are to listen on all interfaces and the listener
                    # is not on all interfaces, this is an error
                    if "0.0.0.0" not in receiving_connections:
                        raise SpinnmanInvalidParameterException(
                            "local_port", str(local_port),
                            "Another connection is already listening on this"
                            " port")

                    # Normalise the local host
                    local_host = "0.0.0.0"
                else:
                    # If we are to listen to a specific interface, and the
                    # listener is on all interfaces, this is an error
                    if "0.0.0.0" in receiving_connections:
                        raise SpinnmanInvalidPacketException(
                            "local_port and local_host",
                            "{} and {}".format(local_port, local_host))

                # If the type of an existing connection is wrong, this is an
                # error
                if local_host in receiving_connections:
                    connection, listener = receiving_connections[local_host]
                    if not isinstance(connection, connection_class):
                        raise SpinnmanInvalidParameterException(
                            "connection_class", connection_class,
                            "A connection of class {} is already listening on"
                            "this port on all interfaces".format(
                                connection.__class__))

            # If we are here, nothing is listening on this port, so create
            # a connection if there isn't already one, and a listener
            if connection is None:
                connection = connection_class(local_port=local_port,
                                              local_host=local_host)
                self._all_connections.add(connection)

            if listener is None:
                listener = ConnectionListener(connection)
                listener.start()
                receiving_connections[local_host] = (connection, listener)

            listener.add_callback(callback)
            connections_of_class.append((connection, listener))
            return connection

        # If we are here, the local port wasn't specified to try to use an
        # existing connection of the correct class
        if connections_of_class:

            # If local_host is not specified, normalise it
            if local_host is None:
                local_host = "0.0.0.0"

            # Find a connection that matches the local host
            for a_connection, a_listener in connections_of_class:
                if a_connection.local_ip_address == local_host:
                    connection, listener = (a_connection, a_listener)
                    break

        # Create a connection if there isn't already one, and a listener
        if connection is None:
            connection = connection_class(local_host=local_host)
            self._all_connections.add(connection)

        if listener is None:
            listener = ConnectionListener(connection)
            listener.start()
            self._udp_receive_connections_by_port[connection.local_port][
                local_host] = (connection, listener)

        listener.add_callback(callback)
        connections_of_class.append((connection, listener))
        return connection

    @property
    def scamp_connection_selector(self):
        """
        :rtype: MostDirectConnectionSelector
        """
        return self._scamp_connection_selector

    @property
    def bmp_connection(self):
        """
        :rtype: dict(tuple(int,int),MostDirectConnectionSelector)
        """
        return self._bmp_connection_selectors

    def get_heap(self, x, y, heap=SystemVariableDefinition.sdram_heap_address):
        """ Get the contents of the given heap on a given chip

        :param int x: The x-coordinate of the chip
        :param int y: The y-coordinate of the chip
        :param SystemVariableDefinition heap:
            The SystemVariableDefinition which is the heap to read
        :rtype: list(HeapElement)
        """
        process = GetHeapProcess(self._scamp_connection_selector)
        return process.get_heap((x, y), heap)

    def __str__(self):
        return "transceiver object connected to {} with {} connections"\
            .format(self._scamp_connections[0].remote_ip_address,
                    len(self._all_connections))

    def __repr__(self):
        return self.__str__()
