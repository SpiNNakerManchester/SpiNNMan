
# local imports
from spinnman import model_binaries
from spinnman import constants
from spinnman.exceptions import SpinnmanInvalidParameterException, \
    SpinnmanException, SpinnmanIOException, SpinnmanTimeoutException, \
    SpinnmanGenericProcessException, SpinnmanUnexpectedResponseCodeException,\
    SpinnmanUnsupportedOperationException, SpinnmanInvalidPacketException

from spinnman.model import CPUInfos, DiagnosticFilter, MachineDimensions
from spinnman.model.enums import CPUState
from spinnman.messages.scp.abstract_messages import AbstractSCPRequest
from spinnman.messages.scp.impl \
    import BMPSetLed, BMPGetVersion, SetPower
from spinnman.messages.scp.impl \
    import ReadADC, ReadFPGARegister
from spinnman.messages.scp.impl \
    import WriteFPGARegister, IPTagSetTTO
from spinnman.messages.spinnaker_boot import SystemVariableDefinition
from spinnman.messages.spinnaker_boot import SpinnakerBootMessages
from spinnman.messages.scp.impl \
    import ReverseIPTagSet, ReadMemory
from spinnman.messages.scp.impl \
    import CountState, WriteMemory, SetLED
from spinnman.messages.scp.impl \
    import ApplicationRun, SendSignal, AppStop
from spinnman.messages.scp.impl \
    import IPTagSet, IPTagClear, RouterClear
from spinnman.connections import ConnectionListener
from spinnman.connections.abstract_classes \
    import SpinnakerBootReceiver, SpinnakerBootSender
from spinnman.connections.udp_packet_connections \
    import BMPConnection, UDPConnection
from spinnman.connections.abstract_classes \
    import SCPSender, SDPSender, MulticastSender
from spinnman.connections.abstract_classes \
    import SCPReceiver, Listenable
from spinnman.connections.udp_packet_connections \
    import BootConnection, SCAMPConnection
from spinnman.processes import DeAllocSDRAMProcess, GetMachineProcess
from spinnman.processes import GetVersionProcess, MallocSDRAMProcess
from spinnman.processes import WriteMemoryProcess, ReadMemoryProcess
from spinnman.processes import GetCPUInfoProcess, ReadIOBufProcess
from spinnman.processes import ApplicationRunProcess, ExitDPRIProcess
from spinnman.utilities.appid_tracker import AppIdTracker
from spinnman.messages.scp.enums import Signal
from spinnman.messages.scp.enums import PowerCommand
from spinnman.messages.scp.enums import DPRIFlags
from spinnman.processes import SetDPRIPacketTypesProcess
from spinnman.processes import SetDPRIRouterTimeoutProcess
from spinnman.processes import SetDPRIRouterEmergencyTimeoutProcess
from spinnman.processes import ResetDPRICountersProcess
from spinnman.processes import ReadDPRIStatusProcess
from spinnman.processes import WriteMemoryFloodProcess
from spinnman.processes import GetTagsProcess
from spinnman.processes import LoadMultiCastRoutesProcess
from spinnman.processes import GetMultiCastRoutesProcess
from spinnman.processes import SendSingleCommandProcess
from spinnman.processes import ReadRouterDiagnosticsProcess
from spinnman.processes import MostDirectConnectionSelector
from spinnman.utilities import utility_functions

# storage handlers imports
from spinn_storage_handlers.abstract_classes import AbstractDataReader
from spinn_storage_handlers import FileDataReader

# spinnmachine imports
from spinn_machine import CoreSubsets

# general imports
import random
import struct
from threading import Condition
from collections import defaultdict
import logging
import socket
import time
import os

logger = logging.getLogger(__name__)

_SCAMP_NAME = "SC&MP"
_SCAMP_VERSION = (3, 0, 1)

_BMP_NAME = "BC&MP"
_BMP_MAJOR_VERSIONS = [1, 2]

_STANDARD_RETIRES_NO = 3
INITIAL_FIND_SCAMP_RETRIES_COUNT = 3


def create_transceiver_from_hostname(
        hostname, version, bmp_connection_data=None, number_of_boards=None,
        ignore_chips=None, ignore_cores=None, ignored_links=None,
        max_core_id=None, auto_detect_bmp=False, scamp_connections=None,
        boot_port_no=None, max_sdram_size=None):
    """ Create a Transceiver by creating a UDPConnection to the given\
        hostname on port 17893 (the default SCAMP port), and a\
        BootConnection on port 54321 (the default boot port),
        optionally discovering any additional links using the UDPConnection,\
        and then returning the transceiver created with the conjunction of the\
        created UDPConnection and the discovered connections

    :param hostname: The hostname or IP address of the board
    :type hostname: str
    :param number_of_boards: a number of boards expected to be supported, or\
                None, which defaults to a single board
    :type number_of_boards: int or None
    :param ignore_chips: An optional set of chips to ignore in the\
                machine.  Requests for a "machine" will have these chips\
                excluded, as if they never existed.  The processor_ids of\
                the specified chips are ignored.
    :type ignore_chips: set of (int, int) of chips to ignore
    :param ignore_cores: An optional set of cores to ignore in the\
                machine.  Requests for a "machine" will have these cores\
                excluded, as if they never existed.
    :type ignore_cores: set of (int, int, int) of cores to ignore
    :param ignored_links: An optional set of links to ignore in the\
                    machine.  Requests for a "machine" will have these links\
                    excluded, as if they never existed.
    :type ignored_links: set of (int, int, int) of links to ignore
    :param max_core_id: The maximum core id in any discovered machine.\
                Requests for a "machine" will only have core ids up to\
                this value.
    :type max_core_id: int
    :param version: the type of spinnaker board used within the spinnaker\
                machine being used. If a spinn-5 board, then the version\
                will be 5, spinn-3 would equal 3 and so on.
    :param bmp_connection_data: the details of the BMP connections used to\
                boot multi-board systems
    :type bmp_connection_data: iterable\
                :py:class:`spinnman.model.bmp_connection_data.BMPConnectionData`
    :param auto_detect_bmp: True if the BMP of version 4 or 5 boards should be\
                automatically determined from the board IP address
    :type auto_detect_bmp: bool
    :param boot_port_no: the port number used to boot the machine
    :type boot_port_no: int
    :param scamp_connections: the list of connections used for scamp
                communications
    :type scamp_connections: iterable of UDPScampConnections
    :param max_sdram_size: the max size each chip can say it has for SDRAM (\
                mainly used in debugging purposes)
    :type max_sdram_size: int or None
    :return: The created transceiver
    :rtype: :py:class:`spinnman.transceiver.Transceiver`
    :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                communicating with the board
    :raise spinnman.exceptions.SpinnmanInvalidPacketException: If a packet\
                is received that is not in the valid format
    :raise spinnman.exceptions.SpinnmanInvalidParameterException: If a\
                packet is received that has invalid parameters
    :raise spinnman.exceptions.SpinnmanUnexpectedResponseCodeException: If\
                a response indicates an error during the exchange
    """
    logger.info("Creating transceiver for {}".format(hostname))
    connections = list()

    # if no BMP has been supplied, but the board is a spinn4 or a spinn5
    # machine, then an assumption can be made that the BMP is at -1 on the
    # final value of the IP address
    if (version >= 4 and auto_detect_bmp is True and
            (bmp_connection_data is None or len(bmp_connection_data) == 0)):
        bmp_connection_data = [
            utility_functions.work_out_bmp_from_machine_details(
                hostname, number_of_boards)]

    # handle BMP connections
    if bmp_connection_data is not None:
        for bmp_connection in bmp_connection_data:

            udp_bmp_connection = BMPConnection(
                bmp_connection.cabinet, bmp_connection.frame,
                bmp_connection.boards, remote_host=bmp_connection.ip_address,
                remote_port=bmp_connection.port_num)
            connections.append(udp_bmp_connection)

    if scamp_connections is None:

        # handle the spinnaker connection
        connections.append(SCAMPConnection(remote_host=hostname))

    # handle the boot connection
    connections.append(BootConnection(
        remote_host=hostname, remote_port=boot_port_no))

    return Transceiver(
        version, connections=connections, ignore_chips=ignore_chips,
        ignore_cores=ignore_cores, max_core_id=max_core_id,
        scamp_connections=scamp_connections, max_sdram_size=max_sdram_size)


class Transceiver(object):
    """ An encapsulation of various communications with the spinnaker board.

        The methods of this class are designed to be thread-safe;\
        thus you can make multiple calls to the same (or different) methods\
        from multiple threads and expect each call to work as if it had been\
        called sequentially, although the order of returns is not guaranteed.\
        Note also that with multiple connections to the board, using multiple\
        threads in this way may result in an increase in the overall speed of\
        operation, since the multiple calls may be made separately over the\
        set of given connections.


    """

    def __init__(
            self, version, connections=None, ignore_chips=None,
            ignore_cores=None, ignore_links=None, max_core_id=None,
            scamp_connections=None, max_sdram_size=None):
        """

        :param version: The version of the board being connected to
        :type version: int
        :param connections: An iterable of connections to the board.  If not\
                    specified, no communication will be possible until\
                    connections are found.
        :type connections: iterable of\
                    :py:class:`spinnman.connections.abstract_classes.connection.Connection`
        :param ignore_chips: An optional set of chips to ignore in the\
                    machine.  Requests for a "machine" will have these chips\
                    excluded, as if they never existed.  The processor_ids of\
                    the specified chips are ignored.
        :type ignore_chips: set of (int, int of chips to ignore
        :param ignore_cores: An optional set of cores to ignore in the\
                    machine.  Requests for a "machine" will have these cores\
                    excluded, as if they never existed.
        :type ignore_cores: set of (int, int, int) of cores to ignore
        :param ignore_links: An optional set of links to ignore in the\
                    machine.  Requests for a "machine" will have these links\
                    excluded, as if they never existed.
        :type ignore_links: set of (int, int, int) of links to ignore
        :param max_core_id: The maximum core id in any discovered machine.\
                    Requests for a "machine" will only have core ids up to and\
                    including this value.
        :type max_core_id: int
        :param max_sdram_size: the max size each chip can say it has for SDRAM\
                (mainly used in debugging purposes)
        :type max_sdram_size: int or None
        :param scamp_connections: a list of scamp connection data or None
        :type scamp_connections: list of \
                :py:class:`spinnman.connections.socket_address_with_chip.SocketAddress_With_Chip`
                 or None
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    communicating with the board, or if no connections to the\
                    board can be found (if connections is None)
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If a packet\
                    is received that is not in the valid format
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If a\
                    packet is received that has invalid parameters
        :raise spinnman.exceptions.SpinnmanUnexpectedResponseCodeException: If\
                    a response indicates an error during the exchange
        """

        # Place to keep the current machine
        self._version = version
        self._machine = None
        self._width = None
        self._height = None
        self._ignore_chips = ignore_chips if ignore_chips is not None else {}
        self._ignore_cores = ignore_cores if ignore_cores is not None else {}
        self._ignore_links = ignore_links if ignore_links is not None else {}
        self._max_core_id = max_core_id
        self._max_sdram_size = max_sdram_size
        self._iobuf_size = None
        self._app_id_tracker = None

        # Place to keep the identity of the re-injector core on each chip,
        # indexed by chip x and y coordinates
        self._reinjector_cores = None
        self._reinjection_running = False
        self._reinjector_app_id = None

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

        # A list of boot receive connections - these are used to
        # listen for the pre-boot board identifiers
        self._boot_receive_connections = list()

        # A dict of port -> dict of ip address -> (connection, listener)
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

        # A dict of ip address -> SCAMP connection
        # These are those that can be used for setting up IP Tags
        self._udp_scamp_connections = dict()

        # A list of all connections that can be used to send and receive SCP
        # messages for SCAMP interaction
        self._scamp_connections = list()

        # if there has been scamp connections given, build them
        if scamp_connections is not None:
            for socket_address in scamp_connections:
                new_connection = SCAMPConnection(
                    remote_host=socket_address.hostname,
                    remote_port=socket_address.port_num,
                    chip_x=socket_address.chip_x,
                    chip_y=socket_address.chip_y)
                connections.append(new_connection)

        # The BMP connections
        self._bmp_connections = list()

        # build connection selectors for the processes.
        self._bmp_connection_selectors = dict()
        self._scamp_connection_selector = None

        # filter connections and build connection selectors.
        self._sort_out_connections(connections)

        # The nearest neighbour start id and lock
        self._next_nearest_neighbour_id = 2
        self._next_nearest_neighbour_condition = Condition()

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

    def _sort_out_connections(self, connections):

        for connection in connections:

            # locate the only boot send connection
            if isinstance(connection, SpinnakerBootSender):
                if self._boot_send_connection is not None:
                    raise SpinnmanInvalidParameterException(
                        "connections", "[... {} ...]".format(connection),
                        "Only a single SpinnakerBootSender can be"
                        " specified")
                else:
                    self._boot_send_connection = connection

            # locate any boot receiver connections
            if isinstance(connection, SpinnakerBootReceiver):
                self._boot_receive_connections.append(connection)

            # Locate any connections listening on a UDP port
            if isinstance(connection, UDPConnection):
                self._udp_receive_connections_by_port[connection.local_port][
                    connection.local_ip_address] = (connection, None)
                if isinstance(connection, Listenable):
                    self._udp_listenable_connections_by_class[
                        connection.__class__].append((connection, None))

            # Locate any connections that can send SCP
            # (that are not BMP connections)
            if (isinstance(connection, SCPSender) and
                    not isinstance(connection, BMPConnection)):
                self._scp_sender_connections.append(connection)

            # Locate any connections that can send SDP
            if isinstance(connection, SDPSender):
                self._sdp_sender_connections.append(connection)

            # Locate any connections that can send Multicast
            if isinstance(connection, MulticastSender):
                self._multicast_sender_connections.append(connection)

            # Locate any connections that can send and receive SCP
            if (isinstance(connection, SCPSender) and
                    isinstance(connection, SCPReceiver)):

                # If it is a BMP connection, add it here
                if isinstance(connection, BMPConnection):
                    self._bmp_connections.append(connection)
                    self._bmp_connection_selectors[
                        (connection.cabinet, connection.frame)] = \
                        MostDirectConnectionSelector(None, [connection])
                else:
                    self._scamp_connections.append(connection)

                    # If also a UDP connection, add it here (for IP tags)
                    if isinstance(connection, UDPConnection):
                        board_address = connection.remote_ip_address
                        self._udp_scamp_connections[board_address] = connection

        # update the transceiver with the connection selectors.
        self._scamp_connection_selector = MostDirectConnectionSelector(
            self._machine, self._scamp_connections)

    def _check_bmp_connections(self):
        """ Check that the BMP connections are actually connected to valid BMPs

        :rtype: None
        :raise SpinnmanIOException: when the connection is not linked to a BMP
        """
        # check that the UDP BMP connection is actually connected to a BMP
        #  via the sver command
        for connection in self._bmp_connections:

            # try to send a BMP sver to check if it responds as expected
            try:
                version_info = self.get_scamp_version(
                    connection.chip_x, connection.chip_y,
                    self._bmp_connection_selectors[(connection.cabinet,
                                                    connection.frame)])
                fail_version_name = version_info.name != _BMP_NAME
                fail_version_num = \
                    version_info.version_number[0] not in _BMP_MAJOR_VERSIONS
                if fail_version_name or fail_version_num:
                    raise SpinnmanIOException(
                        "The BMP at {} is running {}"
                        " {} which is incompatible with this transceiver, "
                        "required version is {} {}".format(
                            connection.remote_ip_address,
                            version_info.name,
                            version_info.version_string,
                            _BMP_NAME, _BMP_MAJOR_VERSIONS))

                logger.info("Using BMP at {} with version {} {}".format(
                    connection.remote_ip_address, version_info.name,
                    version_info.version_string))

            # If it fails to respond due to timeout, maybe that the connection
            # isn't valid
            except SpinnmanTimeoutException:
                raise SpinnmanException(
                    "BMP connection to {} is not responding".format(
                        connection.remote_ip_address))

    def _try_sver_though_scamp_connection(self, connection_selector, retries):
        """ Try to query 0, 0 for SVER through a given connection

        :param connection_selector: the connection selector to use
        :param retries: how many attempts to do before giving up
        :return: True if a valid response is received, False otherwise
        """
        current_retries = retries
        while current_retries > 0:
            try:
                self.get_scamp_version(connection_selector=connection_selector)
                return True
            except SpinnmanGenericProcessException:
                current_retries -= 1
            except SpinnmanTimeoutException:
                current_retries -= 1
            except SpinnmanUnexpectedResponseCodeException:
                current_retries -= 1
            except SpinnmanIOException:
                return False
        return False

    def _get_chip_execute_lock(self, x, y):
        """ Get a lock for executing an executable on a chip
        """

        # Check if there is a lock for the given chip
        self._chip_execute_lock_condition.acquire()
        if not (x, y) in self._chip_execute_locks:
            chip_lock = Condition()
            self._chip_execute_locks[(x, y)] = chip_lock
        else:
            chip_lock = self._chip_execute_locks[(x, y)]
        self._chip_execute_lock_condition.release()

        # Get the lock for the chip
        chip_lock.acquire()

        # Increment the lock counter (used for the flood lock)
        self._chip_execute_lock_condition.acquire()
        self._n_chip_execute_locks += 1
        self._chip_execute_lock_condition.release()

    def _release_chip_execute_lock(self, x, y):
        """ Release the lock for executing on a chip
        """

        # Get the chip lock
        self._chip_execute_lock_condition.acquire()
        chip_lock = self._chip_execute_locks[(x, y)]

        # Release the chip lock
        chip_lock.release()

        # Decrement the lock and notify
        self._n_chip_execute_locks -= 1
        self._chip_execute_lock_condition.notify_all()
        self._chip_execute_lock_condition.release()

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

        :param connections: the list of connections to locate a random one from
        :type connections: a iterable of Abstract connection
        :return: a connection object
        """
        if len(connections) == 0:
            return None
        pos = random.randint(0, len(connections) - 1)
        return connections[pos]

    def send_scp_message(
            self, message, connection=None):
        """ Sends an SCP message, without expecting a response

        :param message: The message to send
        :type message:\
                    :py:class:`spinnman.messages.scp.abstract_scp_request.AbstractSCPRequest`
        :param connection: The connection to use
        :type connection:\
                    :py:class:`spinnman.connections.abstract_classes.connection.Connection`
        :return: The received response, or the callback if get_callback is True
        :rtype:\
                    :py:class:`spinnman.messages.scp.abstract_scp_response.AbstractSCPResponse`
        :raise spinnman.exceptions.SpinnmanTimeoutException: If there is a\
                    timeout before a message is received
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If one\
                    of the fields of the received message is invalid
        :raise spinnman.exceptions.SpinnmanInvalidPacketException:
                    * If the message is not a recognised packet type
                    * If a packet is received that is not a valid response
        :raise spinnman.exceptions.SpinnmanUnsupportedOperationException: If\
                    no connection can send the type of message given
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    sending the message or receiving the response
        :raise spinnman.exceptions.SpinnmanUnexpectedResponseCodeException: If\
                    the response is not one of the expected codes
        """
        if connection is None:
            connection_to_use = self._get_random_connection(
                self._scp_sender_connections)
        else:
            connection_to_use = connection
        connection_to_use.send_scp_request(message)

    def send_sdp_message(self, message, connection=None):
        """ Sends an SDP message using one of the connections.

        :param message: The message to send
        :type message: spinnman.messages.sdp.SDPMessage
        :param connection: An optional connection to use
        :type connection:\
            :py:class:`spinnman.connections.abstract_classes.connection.Connection`
        :rtype: None
        """
        if connection is None:
            connection_to_use = self._get_random_connection(
                self._sdp_sender_connections)
        else:
            connection_to_use = connection
        connection_to_use.send_sdp_message(message)

    def send_multicast_message(self, x, y, multicast_message, connection=None):
        """ Sends a multicast message to the board (currently unsupported)

        :param x: The x-coordinate of the chip where the message should first\
                    arrive on the board
        :type x: int
        :param y: The y-coordinate of the chip where the message should first\
                    arrive on the board
        :type y: int
        :param multicast_message: A multicast message to send
        :type multicast_message:\
            :py:class:`spinnman.messages.multicast_message.MulticastMessage`
        :param connection: A specific connection over which to send the\
                    message.  If not specified, an appropriate connection is\
                    chosen automatically
        :type connection:\
            :py:class:`spinnman.connections.abstract_classes.multicast_sender.MulticastSender`
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    communicating with the board
        :raise spinnman.exceptions.SpinnmanUnsupportedOperationException:
                    * If there is no connection that supports sending over\
                      multicast (or the given connection does not)
                    * If there is no connection that can make the packet\
                      arrive at the selected chip (ignoring routing tables)
        """
        raise SpinnmanUnsupportedOperationException(
            "This operation is currently not supported in spinnman.")

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
            self._ignore_cores, self._ignore_links, self._max_core_id,
            self._max_sdram_size)
        self._machine = get_machine_process.get_machine_details(
            version_info.x, version_info.y, self._width, self._height)

        # update the scamp selector with the machine
        self._scamp_connection_selector.set_machine(self._machine)

        # update the scamp connections replacing any x and y with the default
        # SCP request params with the boot chip coordinates
        for connection in self._scamp_connections:
            if (connection.chip_x ==
                    AbstractSCPRequest.DEFAULT_DEST_X_COORD) and \
                    (connection.chip_y ==
                     AbstractSCPRequest.DEFAULT_DEST_Y_COORD):
                connection.update_chip_coordinates(
                    self._machine.boot_x, self._machine.boot_y)

        # Work out and add the spinnaker links and FPGA links
        self._machine.add_spinnaker_links(self._version)
        self._machine.add_fpga_links(self._version)

        # TODO: Actually get the existing APP_IDs in use
        self._app_id_tracker = AppIdTracker()

        logger.info("Detected a machine on ip address {} which has {}"
                    .format(self._boot_send_connection.remote_ip_address,
                            self._machine.cores_and_link_output_string()))

    def discover_scamp_connections(self):
        """ Find connections to the board and store these for future use.\
            Note that connections can be empty, in which case another local\
            discovery mechanism will be used.  Note that an exception will be\
            thrown if no initial connections can be found to the board.

        :return: An iterable of discovered connections, not including the\
                    initially given connections in the constructor
        :rtype: iterable of\
            :py:class:`spinnman.connections.abstract_classes.connection.Connection`
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    communicating with the board
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If a packet\
                    is received that is not in the valid format
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If a\
                    packet is received that has invalid parameters
        :raise spinnman.exceptions.SpinnmanUnexpectedResponseCodeException: If\
                    a response indicates an error during the exchange
        """

        # Currently, this only finds other UDP connections given a connection
        # that supports SCP - this is done via the machine
        if len(self._scamp_connections) == 0:
            return list()

        # if the machine hasn't been created, create it
        if self._machine is None:
            self._update_machine()

        # Find all the new connections via the machine Ethernet-connected chips
        new_connections = list()
        for chip in self._machine.ethernet_connected_chips:
            if chip.ip_address not in self._udp_scamp_connections:
                new_connection = self._search_for_proxies(chip)

                # if no data, no proxy
                if new_connection is None:
                    new_connection = SCAMPConnection(
                        remote_host=chip.ip_address, chip_x=chip.x,
                        chip_y=chip.y)
                    new_connections.append(new_connection)
                    self._udp_scamp_connections[chip.ip_address] = \
                        new_connection
                    self._scamp_connections.append(new_connection)
                else:

                    # proxy, needs an adjustment
                    if (new_connection.remote_ip_address in
                            self._udp_scamp_connections):
                        del self._udp_scamp_connections[
                            new_connection.remote_ip_address]
                    self._udp_scamp_connections[chip.ip_address] = \
                        new_connection

                # check if it works
                if self._try_sver_though_scamp_connection(
                        MostDirectConnectionSelector(
                            None, [new_connection]), _STANDARD_RETIRES_NO):
                    self._scp_sender_connections.append(new_connection)
                    self._all_connections.add(new_connection)
                else:
                    logger.warn(
                        "Additional Ethernet connection on {} at chip {}, {}"
                        " cannot be contacted"
                        .format(chip.ip_address, chip.x, chip.y))

        # Update the connection queues after finding new connections
        return new_connections

    def _search_for_proxies(self, chip):
        """ Looks for an entry within the UDP scamp connections which is\
            linked to a given chip

        :param chip: the chip to locate
        :rtype: None
        """
        for connection in self._scamp_connections:
            if connection.chip_x == chip.x and connection.chip_y == chip.y:
                return connection
        return None

    def get_connections(self):
        """ Get the currently known connections to the board, made up of those\
            passed in to the transceiver and those that are discovered during\
            calls to discover_connections.  No further discovery is done here.

        :return: An iterable of connections known to the transceiver
        :rtype: iterable of\
            :py:class:`spinnman.connections.abstract_classes.connection.Connection`
        :raise None: No known exceptions are raised
        """
        return self._all_connections

    def get_machine_dimensions(self):
        """ Get the maximum chip x-coordinate and maximum chip y-coordinate of\
            the chips in the machine

        :return: The dimensions of the machine
        :rtype: :py:class:`spinnman.model.machine_dimensions.MachineDimensions`
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    communicating with the board
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If a packet\
                    is received that is not in the valid format
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If a\
                    packet is received that has invalid parameters
        :raise spinnman.exceptions.SpinnmanUnexpectedResponseCodeException: If\
                    a response indicates an error during the exchange
        """
        if self._width is None or self._height is None:
            height_item = SystemVariableDefinition.y_size
            self._height, self._width = struct.unpack_from(
                "<BB",
                str(self.read_memory(
                    AbstractSCPRequest.DEFAULT_DEST_X_COORD,
                    AbstractSCPRequest.DEFAULT_DEST_Y_COORD,
                    (constants.SYSTEM_VARIABLE_BASE_ADDRESS +
                        height_item.offset),
                    2)))
        return MachineDimensions(self._width, self._height)

    def get_machine_details(self):
        """ Get the details of the machine made up of chips on a board and how\
            they are connected to each other.

        :return: A machine description
        :rtype: :py:class:`spinn_machine.Machine`
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    communicating with the board
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If a packet\
                    is received that is not in the valid format
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If a\
                    packet is received that has invalid parameters
        :raise spinnman.exceptions.SpinnmanUnexpectedResponseCodeException: If\
                    a response indicates an error during the exchange
        """
        if self._machine is None:
            self._update_machine()
        return self._machine

    @property
    def app_id_tracker(self):
        """ Get the app id tracker for this transceiver

        :rtype: :py:class:`spinnman.utilities.appid_tracker.AppIdTracker`
        """
        if self._app_id_tracker is None:
            self._update_machine()
        return self._app_id_tracker

    def is_connected(self, connection=None):
        """ Determines if the board can be contacted

        :param connection: The connection which is to be tested.  If none,\
                    all connections will be tested, and the board will be\
                    considered to be connected if any one connection works.
        :type connection:\
            :py:class:`spinnman.connections.abstract_classes.connection.Connection`
        :return: True if the board can be contacted, False otherwise
        :rtype: bool
        :raise None: No known exceptions are raised
        """
        if connection is not None:
            if connection.is_connected():
                return True
            return False
        else:
            for connection in self._scamp_connections:
                if connection.is_connected():
                    return True
            return False

    def get_scamp_version(
            self, chip_x=AbstractSCPRequest.DEFAULT_DEST_X_COORD,
            chip_y=AbstractSCPRequest.DEFAULT_DEST_Y_COORD,
            connection_selector=None):
        """ Get the version of scamp which is running on the board

        :param connection_selector: the connection to send the scamp
            version or none (if none then a random scamp connection is used)
        :type connection_selector: a instance of a
            :py:class:'spinnman.processes.abstract_multi_connection_process_connection_selector.AbstractMultiConnectionProcessConnectionSelector'
        :param chip_x: the chip's x coordinate to query for scamp version
        :type chip_x: int
        :param chip_y: the chip's y coordinate to query for scamp version
        :return: The version identifier
        :rtype: :py:class:`spinnman.model.version_info.VersionInfo`
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    communicating with the board
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If the\
                    timeout is less than 1
        :raise spinnman.exceptions.SpinnmanTimeoutException: If none of the\
                    retries resulted in a response before the timeout\
                    (suggesting that the board is not booted)
        """
        if connection_selector is None:
            connection_selector = self._scamp_connection_selector
        process = GetVersionProcess(connection_selector)
        return process.get_version(x=chip_x, y=chip_y, p=0)

    def boot_board(
            self, number_of_boards=None, width=None, height=None,
            extra_boot_values=None):
        """ Attempt to boot the board.  No check is performed to see if the\
            board is already booted.

        :param number_of_boards: this parameter is deprecated
        :type number_of_boards: int
        :param width: this parameter is deprecated
        :type width: int or None
        :param height: this parameter is deprecated
        :type height: int or None
        :param extra_boot_values: extra values to set during boot
        :type extra_boot_values: dict of SystemVariableDefinition to value
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If the\
                    board version is not known
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    communicating with the board
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

        :param version: The version to test
        :type version: (int, int, int)
        """

        # The major version must match exactly
        if (version[0] != _SCAMP_VERSION[0]):
            return False

        # If the minor version matches, the patch version must be >= the
        # required version
        if (version[1] == _SCAMP_VERSION[1]):
            return version[2] >= _SCAMP_VERSION[2]

        # If the minor version is > than the required version, the patch
        # version is irrelevant
        return (version[1] > _SCAMP_VERSION[1])

    def ensure_board_is_ready(
            self, number_of_boards=None, width=None, height=None,
            n_retries=5, enable_reinjector=True, extra_boot_values=None):
        """ Ensure that the board is ready to interact with this version\
            of the transceiver.  Boots the board if not already booted and\
            verifies that the version of SCAMP running is compatible with\
            this transceiver.

        :param number_of_boards: this parameter is deprecated and will be\
                    ignored
        :type number_of_boards: int
        :param width: this parameter is deprecated and will be ignored
        :type width: int or None
        :param height: this parameter is deprecated and will be ignored
        :type height: int or None
        :param n_retries: The number of times to retry booting
        :type n_retries: int
        :param enable_reinjector: a boolean that allows the reinjector to be\
                    added to the system
        :type enable_reinjector: bool
        :param extra_boot_values: Any additional values to set during boot
        :type extra_boot_values: dict of SystemVariableDefinition to value
        :return: The version identifier
        :rtype: :py:class:`spinnman.model.version_info.VersionInfo`
        :raise: spinnman.exceptions.SpinnmanIOException:
                    * If there is a problem booting the board
                    * If the version of software on the board is not\
                      compatible with this transceiver
        """

        # if the machine sizes not been given, calculate from assumption
        if (width is not None or height is not None or
                number_of_boards is not None):
            logger.warning(
                "The width, height and number_of_boards are no longer"
                " supported, and might be removed in a future version")

        # try to get a scamp version once
        logger.info("Working out if machine is booted")
        if self._machine_off:
            version_info = None
        else:
            version_info = self._try_to_find_scamp_and_boot(
                INITIAL_FIND_SCAMP_RETRIES_COUNT, number_of_boards,
                width, height)

        # If we fail to get a SCAMP version this time, try other things
        if version_info is None and len(self._bmp_connections) > 0:

            # start by powering up each BMP connection
            logger.info("Attempting to power on machine")
            self.power_on_machine()

            # Sleep a bit to let things get going
            time.sleep(2.0)
            logger.info("Attempting to boot machine")

            # retry to get a scamp version, this time trying multiple times
            version_info = self._try_to_find_scamp_and_boot(
                n_retries, number_of_boards, width, height)

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
                constants.IPTAG_TIME_OUT_WAIT_TIMES.TIMEOUT_640_ms.value))

        # If reinjection is enabled, load the reinjector
        if enable_reinjector:
            self.enable_reinjection()

        return version_info

    def _try_to_find_scamp_and_boot(
            self, tries_to_go, number_of_boards, width, height):
        """ Try to detect if SCAMP is running, and if not, boot the machine

        :param tries_to_go: how many attempts should be supported
        :param number_of_boards: the number of boards that this machine \
                is built out of
        :param width: The width of the machine in chips
        :param height: The height of the machine in chips
        :return: version_info
        :raise SpinnmanIOException: If there is a problem communicating with\
                the machine
        """
        version_info = None
        current_tries_to_go = tries_to_go
        while version_info is None and current_tries_to_go > 0:
            try:
                version_info = self.get_scamp_version()
                if (version_info.x ==
                        AbstractSCPRequest.DEFAULT_DEST_X_COORD) and \
                        (version_info.y ==
                         AbstractSCPRequest.DEFAULT_DEST_Y_COORD):
                    version_info = None
                    time.sleep(0.1)
            except SpinnmanGenericProcessException as e:
                if isinstance(e.exception, SpinnmanTimeoutException):
                    logger.info("Attempting to boot machine")
                    self.boot_board(number_of_boards, width, height)
                    current_tries_to_go -= 1
                elif isinstance(e.exception, SpinnmanIOException):
                    raise SpinnmanIOException(
                        "Failed to communicate with the machine")
                else:
                    raise
            except SpinnmanTimeoutException:
                logger.info("Attempting to boot machine")
                self.boot_board(number_of_boards, width, height)
                current_tries_to_go -= 1
            except SpinnmanIOException:
                raise SpinnmanIOException(
                    "Failed to communicate with the machine")

        # The last thing we tried was booting, so try again to get the version
        if version_info is None:
            try:
                version_info = self.get_scamp_version()
                if (version_info.x ==
                        AbstractSCPRequest.DEFAULT_DEST_X_COORD) and \
                        (version_info.y ==
                         AbstractSCPRequest.DEFAULT_DEST_Y_COORD):
                    version_info = None
            except SpinnmanException:
                pass
        if version_info is not None:
            logger.info("Found board with version {}".format(version_info))
        return version_info

    def get_cpu_information(self, core_subsets=None):
        """ Get information about the processors on the board

        :param core_subsets: A set of chips and cores from which to get\
                    the information.  If not specified, the information from\
                    all of the cores on all of the chips on the board are\
                    obtained
        :type core_subsets: :py:class:`spinn_machine.CoreSubsets`
        :return: An iterable of the cpu information for the selected cores, or\
                    all cores if core_subsets is not specified
        :rtype: iterable of :py:class:`spinnman.model.CPUInfo`
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    communicating with the board
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If a packet\
                    is received that is not in the valid format
        :raise spinnman.exceptions.SpinnmanInvalidParameterException:
                    * If chip_and_cores contains invalid items
                    * If a packet is received that has invalid parameters
        :raise spinnman.exceptions.SpinnmanUnexpectedResponseCodeException: If\
                    a response indicates an error during the exchange
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
        return struct.unpack_from(
            data_item.data_type.struct_code,
            str(self.read_memory(
                x, y,
                constants.SYSTEM_VARIABLE_BASE_ADDRESS + data_item.offset,
                data_item.data_type.value)))[0]

    def get_user_0_register_address_from_core(self, x, y, p):
        """ Get the address of user 0 for a given processor on the board

        :param x: the x-coordinate of the chip containing the processor
        :param y: the y-coordinate of the chip containing the processor
        :param p: The id of the processor to get the user 0 address from
        :type x: int
        :type y: int
        :type p: int
        :return: The address for user 0 register for this processor
        :rtype: int
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If a packet\
                    is received that is not in the valid format
        :raise spinnman.exceptions.SpinnmanInvalidParameterException:
                    * If x, y, p is not a valid processor
                    * If a packet is received that has invalid parameters
        :raise spinnman.exceptions.SpinnmanUnexpectedResponseCodeException: If\
                    a response indicates an error during the exchange
        """
        return (
            utility_functions.get_vcpu_address(p) +
            constants.CPU_USER_0_START_ADDRESS)

    def get_user_1_register_address_from_core(self, x, y, p):
        """ Get the address of user 1 for a given processor on the board

        :param x: the x-coordinate of the chip containing the processor
        :param y: the y-coordinate of the chip containing the processor
        :param p: The id of the processor to get the user 1 address from
        :type x: int
        :type y: int
        :type p: int
        :return: The address for user 1 register for this processor
        :rtype: int
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If a packet\
                    is received that is not in the valid format
        :raise spinnman.exceptions.SpinnmanInvalidParameterException:
                    * If x, y, p is not a valid processor
                    * If a packet is received that has invalid parameters
        :raise spinnman.exceptions.SpinnmanUnexpectedResponseCodeException: If\
                    a response indicates an error during the exchange
        """
        return (
            utility_functions.get_vcpu_address(p) +
            constants.CPU_USER_1_START_ADDRESS)

    def get_user_2_register_address_from_core(self, x, y, p):
        """ Get the address of user 2 for a given processor on the board

        :param x: the x-coordinate of the chip containing the processor
        :param y: the y-coordinate of the chip containing the processor
        :param p: The id of the processor to get the user 0 address from
        :type x: int
        :type y: int
        :type p: int
        :return: The address for user 0 register for this processor
        :rtype: int
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If a packet\
                    is received that is not in the valid format
        :raise spinnman.exceptions.SpinnmanInvalidParameterException:
                    * If x, y, p is not a valid processor
                    * If a packet is received that has invalid parameters
        :raise spinnman.exceptions.SpinnmanUnexpectedResponseCodeException: If\
                    a response indicates an error during the exchange
        """
        return (
            utility_functions.get_vcpu_address(p) +
            constants.CPU_USER_2_START_ADDRESS)

    def get_cpu_information_from_core(self, x, y, p):
        """ Get information about a specific processor on the board

        :param x: The x-coordinate of the chip containing the processor
        :type x: int
        :param y: The y-coordinate of the chip containing the processor
        :type y: int
        :param p: The id of the processor to get the information about
        :type p: int
        :return: The cpu information for the selected core
        :rtype: :py:class:`spinnman.model.cpu_info.CPUInfo`
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    communicating with the board
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If a packet\
                    is received that is not in the valid format
        :raise spinnman.exceptions.SpinnmanInvalidParameterException:
                    * If x, y, p is not a valid processor
                    * If a packet is received that has invalid parameters
        :raise spinnman.exceptions.SpinnmanUnexpectedResponseCodeException: If\
                    a response indicates an error during the exchange
        """

        core_subsets = CoreSubsets()
        core_subsets.add_processor(x, y, p)
        return list(self.get_cpu_information(core_subsets))[0]

    def get_iobuf(self, core_subsets=None):
        """ Get the contents of the IOBUF buffer for a number of processors

        :param core_subsets: A set of chips and cores from which to get\
                    the buffers.  If not specified, the buffers from\
                    all of the cores on all of the chips on the board are\
                    obtained
        :type core_subsets: :py:class:`spinn_machine.CoreSubsets`
        :return: An iterable of the buffers, which may not be in the order\
                    of core_subsets
        :rtype: iterable of :py:class:`spinnman.model.IOBuffer`
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    communicating with the board
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If a packet\
                    is received that is not in the valid format
        :raise spinnman.exceptions.SpinnmanInvalidParameterException:
                    * If chip_and_cores contains invalid items
                    * If a packet is received that has invalid parameters
        :raise spinnman.exceptions.SpinnmanUnexpectedResponseCodeException: If\
                    a response indicates an error during the exchange
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

        :param x: chip x coord to write new watch dog param to
        :type x: int
        :param y: chip y coord to write new watch dog param to
        :type y: int
        :param watch_dog:\
            Either a boolean indicating whether to enable (True) or \
            disable (False) the watch dog timer or an int value to set the \
            timer count to
        :type watch_dog: boolean or int
        :rtype: None
        """

        # build what we expect it to be
        value_to_set = watch_dog
        if isinstance(watch_dog, bool):
            if not watch_dog:
                value_to_set = 0
            else:
                value_to_set = \
                    SystemVariableDefinition.software_watchdog_count.default

        # build data holder
        data = struct.pack("B", value_to_set)

        # write data
        base_address = (
            constants.SYSTEM_VARIABLE_BASE_ADDRESS +
            SystemVariableDefinition.software_watchdog_count.offset)

        self.write_memory(
            x=x, y=y, base_address=base_address, data=data)

    def set_watch_dog(self, watch_dog):
        """ Enable, disable or set the value of the watch dog timer

        :param watch_dog:\
            Either a boolean indicating whether to enable (True) or \
            disable (False) the watch dog timer or an int value to set the \
            timer count to
        :type watch_dog: boolean or int
        :rtype: None
        """
        if self._machine is None:
            self._update_machine()
        for x, y in self._machine.chip_coordinates:
            self.set_watch_dog_on_chip(x, y, watch_dog)

    def get_iobuf_from_core(self, x, y, p):
        """ Get the contents of IOBUF for a given core

        :param x: The x-coordinate of the chip containing the processor
        :type x: int
        :param y: The y-coordinate of the chip containing the processor
        :type y: int
        :param p: The id of the processor to get the IOBUF for
        :type p: int
        :return: An IOBUF buffer
        :rtype: :py:class:`spinnman.model.IOBuffer`
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    communicating with the board
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If a packet\
                    is received that is not in the valid format
        :raise spinnman.exceptions.SpinnmanInvalidParameterException:
                    * If chip_and_cores contains invalid items
                    * If a packet is received that has invalid parameters
        :raise spinnman.exceptions.SpinnmanUnexpectedResponseCodeException: If\
                    a response indicates an error during the exchange
        """
        core_subsets = CoreSubsets()
        core_subsets.add_processor(x, y, p)
        return self.get_iobuf(core_subsets).next()

    def get_core_state_count(self, app_id, state):
        """ Get a count of the number of cores which have a given state

        :param app_id: The id of the application from which to get the count.
        :type app_id: int
        :param state: The state count to get
        :type state: :py:class:`spinnman.model.CPUState`
        :return: A count of the cores with the given status
        :rtype: int
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    communicating with the board
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If a packet\
                    is received that is not in the valid format
        :raise spinnman.exceptions.SpinnmanInvalidParameterException:
                    * If state is not a valid status
                    * If app_id is not a valid application id
                    * If a packet is received that has invalid parameters
        :raise spinnman.exceptions.SpinnmanUnexpectedResponseCodeException: If\
                    a response indicates an error during the exchange
        """
        process = SendSingleCommandProcess(self._scamp_connection_selector)
        response = process.execute(CountState(app_id, state))
        return response.count

    def execute(
            self, x, y, processors, executable, app_id, n_bytes=None,
            wait=False, is_filename=False):
        """ Start an executable running on a single core

        :param x: The x-coordinate of the chip on which to run the executable
        :type x: int
        :param y: The y-coordinate of the chip on which to run the executable
        :type y: int
        :param processors: The cores on the chip on which to run the\
                    application
        :type processors: iterable of int
        :param executable: The data that is to be executed.  Should be one of\
                    the following:
                    * An instance of AbstractDataReader
                    * A bytearray
                    * A filename of a file containing the executable (in which\
                      case is_filename must be set to True)
        :type executable:\
                    :py:class:`spinnman.data.abstract_data_reader.AbstractDataReader`\
                    or bytearray or str
        :param app_id: The id of the application with which to associate the\
                    executable
        :type app_id: int
        :param n_bytes: The size of the executable data in bytes.  If not\
                    specified:
                        * If executable is an AbstractDataReader, an error\
                          is raised
                        * If executable is a bytearray, the length of the\
                          bytearray will be used
                        * If executable is an int, 4 will be used
                        * If executable is a str, the length of the file will\
                          be used
        :type n_bytes: int
        :param wait: True if the binary should enter a "wait" state on loading
        :type wait: bool
        :param is_filename: True if executable is a filename
        :type is_filename: bool
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanIOException:
                    * If there is an error communicating with the board
                    * If there is an error reading the executable
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If a packet\
                    is received that is not in the valid format
        :raise spinnman.exceptions.SpinnmanInvalidParameterException:
                    * If x, y, p does not lead to a valid core
                    * If app_id is an invalid application id
                    * If a packet is received that has invalid parameters
        :raise spinnman.exceptions.SpinnmanUnexpectedResponseCodeException: If\
                    a response indicates an error during the exchange
        """

        # Lock against updates
        self._get_chip_execute_lock(x, y)

        # Write the executable
        self.write_memory(
            x, y, 0x67800000, executable, n_bytes, is_filename=is_filename)

        # Request the start of the executable
        process = SendSingleCommandProcess(self._scamp_connection_selector)
        process.execute(
            ApplicationRun(app_id, x, y, processors, wait))

        # Release the lock
        self._release_chip_execute_lock(x, y)

    def _get_next_nearest_neighbour_id(self):
        self._next_nearest_neighbour_condition.acquire()
        next_nearest_neighbour_id = self._next_nearest_neighbour_id
        self._next_nearest_neighbour_id = \
            (self._next_nearest_neighbour_id + 1) % 127
        self._next_nearest_neighbour_condition.release()
        return next_nearest_neighbour_id

    def execute_flood(
            self, core_subsets, executable, app_id, n_bytes=None, wait=False,
            is_filename=False):
        """ Start an executable running on multiple places on the board.  This\
            will be optimised based on the selected cores, but it may still\
            require a number of communications with the board to execute.

        :param core_subsets: Which cores on which chips to start the executable
        :type core_subsets: :py:class:`spinn_machine.CoreSubsets`
        :param executable: The data that is to be executed.  Should be one of\
                    the following:
                    * An instance of AbstractDataReader
                    * A bytearray
                    * A filename of an executable (in which case is_filename\
                      must be set to True)
        :type executable:\
                    :py:class:`spinnman.data.abstract_data_reader.AbstractDataReader`\
                    or bytearray or str
        :param app_id: The id of the application with which to associate the\
                    executable
        :type app_id: int
        :param n_bytes: The size of the executable data in bytes.  If not\
                    specified:
                        * If executable is an AbstractDataReader, an error\
                          is raised
                        * If executable is a bytearray, the length of the\
                          bytearray will be used
                        * If executable is an int, 4 will be used
                        * If executable is a str, the length of the file will\
                          be used
        :type n_bytes: int
        :param wait: True if the processors should enter a "wait" state on\
                    loading
        :type wait: bool
        :param is_filename: True if the data is a filename
        :type is_filename: bool
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanIOException:
                    * If there is an error communicating with the board
                    * If there is an error reading the executable
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If a packet\
                    is received that is not in the valid format
        :raise spinnman.exceptions.SpinnmanInvalidParameterException:
                    * If one of the specified cores is not valid
                    * If app_id is an invalid application id
                    * If a packet is received that has invalid parameters
                    * If data is an AbstractDataReader but n_bytes is not\
                      specified
                    * If data is an int and n_bytes is more than 4
                    * If n_bytes is less than 0
        :raise spinnman.exceptions.SpinnmanUnexpectedResponseCodeException: If\
                    a response indicates an error during the exchange
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

        :param executable_targets: The binaries to be executed and the cores\
                    to execute them on
        :type executable_targets:\
                    :py:class:`spinnman.model.executable_targets.ExecutableTargets`
        :param app_id: The app_id to give this application
        :type app_id: int
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
            raise SpinnmanException(
                "Only {} of {} cores reached ready state".format(
                    count, executable_targets.total_processors))

        # Send a signal telling the application to start
        self.send_signal(app_id, Signal.START)

    def power_on_machine(self):
        """ Power on the whole machine
        """
        if len(self._bmp_connections) == 0:
            logger.warn("No BMP connections, so can't power on")
        for bmp_connection in self._bmp_connections:
            self.power_on(bmp_connection.boards, bmp_connection.cabinet,
                          bmp_connection.frame)

    def power_on(self, boards=0, cabinet=0, frame=0):
        """ Power on a set of boards in the machine

        :param boards: The board or boards to power on
        :param cabinet: the id of the cabinet containing the frame, or 0 \
                if the frame is not in a cabinet
        :param frame: the id of the frame in the cabinet containing the\
                board(s), or 0 if the board is not in a frame
        """
        self._power(PowerCommand.POWER_ON, boards, cabinet, frame)

    def power_off_machine(self):
        """ Power off the whole machine
        """
        self._reinjection_running = False
        if len(self._bmp_connections) == 0:
            logger.warn("No BMP connections, so can't power off")
        for bmp_connection in self._bmp_connections:
            self.power_off(bmp_connection.boards, bmp_connection.cabinet,
                           bmp_connection.frame)

    def power_off(self, boards=0, cabinet=0, frame=0):
        """ Power off a set of boards in the machine

        :param boards: The board or boards to power off
        :param cabinet: the id of the cabinet containing the frame, or 0 \
                if the frame is not in a cabinet
        :param frame: the id of the frame in the cabinet containing the\
                board(s), or 0 if the board is not in a frame
        """
        self._power(PowerCommand.POWER_OFF, boards, cabinet, frame)
        self._reinjection_running = False

    def _bmp_connection(self, cabinet, frame):
        if (cabinet, frame) not in self._bmp_connection_selectors:
            raise SpinnmanInvalidParameterException(
                "cabinet and frame", "{} and {}".format(cabinet, frame),
                "Unknown combination")
        return self._bmp_connection_selectors[(cabinet, frame)]

    def _power(self, power_command, boards=0, cabinet=0, frame=0):
        """ Send a power request to the machine

        :param power_command: The power command to send
        :param boards: The board or boards to send the command to
        :param cabinet: the id of the cabinet containing the frame, or 0 \
                if the frame is not in a cabinet
        :param frame: the id of the frame in the cabinet containing the\
                board(s), or 0 if the board is not in a frame
        :rtype: None
        """
        process = SendSingleCommandProcess(
            self._bmp_connection(cabinet, frame),
            timeout=constants.BMP_POWER_ON_TIMEOUT, n_retries=0)
        process.execute(SetPower(power_command, boards))
        self._machine_off = power_command == PowerCommand.POWER_OFF

    def set_led(self, led, action, board, cabinet, frame):
        """ Set the LED state of a board in the machine

        :param led:  Number of the LED or an iterable of LEDs to set the\
                state of (0-7)
        :type led: int or iterable of int
        :param action: State to set the LED to, either on, off or toggle
        :type action:\
                :py:class:`spinnman.messages.scp.scp_led_action.SCPLEDAction`
        :param board: Specifies the board to control the LEDs of. This may \
                also be an iterable of multiple boards (in the same frame).\
                The command will actually be sent to the first board in the\
                iterable.
        :type board: int or iterable
        :param cabinet: the cabinet this is targeting
        :type cabinet: int
        :param frame: the frame this is targeting
        :type frame: int
        :rtype: None
        """
        process = SendSingleCommandProcess(
            self._bmp_connection(cabinet, frame))
        process.execute(BMPSetLed(led, action, board))

    def read_fpga_register(self, fpga_num, register, cabinet, frame, board):
        """

        :param fpga_num: FPGA number (0, 1 or 2) to communicate with.
        :type fpga_num: int
        :param register: Register address to read to (will be rounded down to
                the nearest 32-bit word boundary).
        :type register: int
        :param cabinet: cabinet: the cabinet this is targeting
        :type cabinet: int
        :param frame: the frame this is targeting
        :type frame: int
        :param board: which board to request the FPGA register from
        :return: the register data
        """
        process = SendSingleCommandProcess(
            self._bmp_connection(cabinet, frame))
        response = process.execute(
            ReadFPGARegister(fpga_num, register, board))
        return response.fpga_register

    def write_fpga_register(self, fpga_num, register, value, cabinet, frame,
                            board):
        """

        :param fpga_num: FPGA number (0, 1 or 2) to communicate with.
        :type fpga_num: int
        :param register: Register address to read to (will be rounded down to
                the nearest 32-bit word boundary).
        :type register: int
        :param value: the value to write into the FPGA register
        :type value: int
        :param cabinet: cabinet: the cabinet this is targeting
        :type cabinet: int
        :param frame: the frame this is targeting
        :type frame: int
        :param board: which board to write the FPGA register to
        :rtype: None
        """
        process = SendSingleCommandProcess(
            self._bmp_connection(cabinet, frame))
        process.execute(
            WriteFPGARegister(fpga_num, register, value, board))

    def read_adc_data(self, board, cabinet, frame):
        """ Read the BMP ADC data

        :param cabinet: cabinet: the cabinet this is targeting
        :type cabinet: int
        :param frame: the frame this is targeting
        :type frame: int
        :param board: which board to request the ADC data from
        :return: the FPGA's ADC data object
        """
        process = SendSingleCommandProcess(
            self._bmp_connection(cabinet, frame))
        response = process.execute(ReadADC(board))
        return response.adc_info

    def read_bmp_version(self, board, cabinet, frame):
        """ Read the BMP version

        :param cabinet: cabinet: the cabinet this is targeting
        :type cabinet: int
        :param frame: the frame this is targeting
        :type frame: int
        :param board: which board to request the data from
        :return: the sver from the BMP
        """
        process = SendSingleCommandProcess(
            self._bmp_connection(cabinet, frame))
        response = process.execute(BMPGetVersion(board))
        return response.version_info

    def write_memory(self, x, y, base_address, data, n_bytes=None, offset=0,
                     cpu=0, is_filename=False):
        """ Write to the SDRAM on the board

        :param x: The x-coordinate of the chip where the memory is to be\
                    written to
        :type x: int
        :param y: The y-coordinate of the chip where the memory is to be\
                    written to
        :type y: int
        :param base_address: The address in SDRAM where the region of memory\
                    is to be written
        :type base_address: int
        :param data: The data to write.  Should be one of the following:
                    * An instance of AbstractDataReader
                    * A bytearray
                    * A single integer - will be written using little-endian\
                      byte ordering
                    * A filename of a data file (in which case is_filename\
                      must be set to True)
        :type data:\
                    :py:class:`spinnman.data.abstract_data_reader.AbstractDataReader`\
                    or bytearray or int or str
        :param n_bytes: The amount of data to be written in bytes.  If not\
                    specified:
                        * If data is an AbstractDataReader, an error is raised
                        * If data is a bytearray, the length of the bytearray\
                          will be used
                        * If data is an int, 4 will be used
                        * If data is a str, the length of the file will be used
        :type n_bytes: int
        :param offset: The offset from which the valid data begins
        :type offset: int
        :param cpu: The optional cpu to write to
        :type cpu: int
        :param is_filename: True if the data is a filename
        :type is_filename: bool
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanIOException:
                    * If there is an error communicating with the board
                    * If there is an error reading the data
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If a packet\
                    is received that is not in the valid format
        :raise spinnman.exceptions.SpinnmanInvalidParameterException:
                    * If x, y does not lead to a valid chip
                    * If a packet is received that has invalid parameters
                    * If base_address is not a positive integer
                    * If data is an AbstractDataReader but n_bytes is not\
                      specified
                    * If data is an int and n_bytes is more than 4
                    * If n_bytes is less than 0
        :raise spinnman.exceptions.SpinnmanUnexpectedResponseCodeException: If\
                    a response indicates an error during the exchange
        """
        process = WriteMemoryProcess(self._scamp_connection_selector)
        if isinstance(data, AbstractDataReader):
            process.write_memory_from_reader(
                x, y, cpu, base_address, data, n_bytes)
        elif isinstance(data, str) and is_filename:
            reader = FileDataReader(data)
            if n_bytes is None:
                n_bytes = os.stat(data).st_size
            process.write_memory_from_reader(
                x, y, cpu, base_address, reader, n_bytes)
            reader.close()
        elif isinstance(data, int):
            data_to_write = struct.pack("<I", data)
            process.write_memory_from_bytearray(
                x, y, cpu, base_address, data_to_write, 0, 4)
        elif isinstance(data, long):
            data_to_write = struct.pack("<Q", data)
            process.write_memory_from_bytearray(
                x, y, cpu, base_address, data_to_write, 0, 8)
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

        :param x: The x-coordinate of the chip whose neighbour is to be\
                    written to
        :type x: int
        :param y: The y-coordinate of the chip whose neighbour is to be\
                    written to
        :type y: int
        :param link: The link index to send the request to (or if BMP, the\
                    FPGA number)
        :type link: int
        :param base_address: The address in SDRAM where the region of memory\
                    is to be written
        :type base_address: int
        :param data: The data to write.  Should be one of the following:
                    * An instance of AbstractDataReader
                    * A bytearray
                    * A single integer - will be written using little-endian\
                      byte ordering
        :type data:\
                    :py:class:`spinnman.data.abstract_data_reader.AbstractDataReader`\
                    or bytearray or int
        :param n_bytes: The amount of data to be written in bytes.  If not\
                    specified:
                        * If data is an AbstractDataReader, an error is raised
                        * If data is a bytearray, the length of the bytearray\
                          will be used
                        * If data is an int, 4 will be used
        :type n_bytes: int
        :param offset: The offset where the valid data starts (if the data is \
                        an int then offset will be ignored and used 0
        :type offset: int
        :param cpu: The cpu to use, typically 0 (or if a BMP, the slot number)
        :type cpu: int
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanIOException:
                    * If there is an error communicating with the board
                    * If there is an error reading the data
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If a packet\
                    is received that is not in the valid format
        :raise spinnman.exceptions.SpinnmanInvalidParameterException:
                    * If x, y does not lead to a valid chip
                    * If a packet is received that has invalid parameters
                    * If base_address is not a positive integer
                    * If data is an AbstractDataReader but n_bytes is not\
                      specified
                    * If data is an int and n_bytes is more than 4
                    * If n_bytes is less than 0
        :raise spinnman.exceptions.SpinnmanUnexpectedResponseCodeException: If\
                    a response indicates an error during the exchange
        """

        process = WriteMemoryProcess(self._scamp_connection_selector)
        if isinstance(data, AbstractDataReader):
            process.write_link_memory_from_reader(
                x, y, cpu, link, base_address, data, n_bytes)
        elif isinstance(data, int):
            data_to_write = struct.pack("<I", data)
            process.write_link_memory_from_bytearray(
                x, y, cpu, link, base_address, data_to_write, 0, 4)
        elif isinstance(data, long):
            data_to_write = struct.pack("<Q", data)
            process.write_link_memory_from_bytearray(
                x, y, cpu, link, base_address, data_to_write, 0, 8)
        else:
            if n_bytes is None:
                n_bytes = len(data)
            process.write_link_memory_from_bytearray(
                x, y, cpu, link, base_address, data, offset, n_bytes)

    def write_memory_flood(
            self, base_address, data, n_bytes=None, offset=0,
            is_filename=False):
        """ Write to the SDRAM of all chips.

        :param base_address: The address in SDRAM where the region of memory\
                    is to be written
        :type base_address: int
        :param data: The data that is to be written.  Should be one of\
                    the following:
                    * An instance of AbstractDataReader
                    * A bytearray or bytestring
                    * A single integer
                    * A file name of a file to read (in which case is_filename\
                      should be set to True)
        :type data:\
                    :py:class:`spinnman.data.abstract_data_reader.AbstractDataReader`\
                    or bytearray or int
        :param n_bytes: The amount of data to be written in bytes.  If not\
                    specified:
                        * If data is an AbstractDataReader, an error is raised
                        * If data is a bytearray, the length of the bytearray\
                          will be used
                        * If data is an int, 4 will be used
                        * If data is a str, the size of the file will be used
        :type n_bytes: int
        :param offset: The offset where the valid data starts, if the data is \
                        a int, then the offset will be ignored and 0 is used.
        :type offset: int
        :param is_filename: True if the data should be interpreted as a file \
                    name
        :type is_filename: bool
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanIOException:
                    * If there is an error communicating with the board
                    * If there is an error reading the executable
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If a packet\
                    is received that is not in the valid format
        :raise spinnman.exceptions.SpinnmanInvalidParameterException:
                    * If one of the specified chips is not valid
                    * If app_id is an invalid application id
                    * If a packet is received that has invalid parameters
        :raise spinnman.exceptions.SpinnmanUnexpectedResponseCodeException: If\
                    a response indicates an error during the exchange
        """

        # Ensure only one flood fill occurs at any one time
        self._flood_write_lock.acquire()

        # Start the flood fill
        nearest_neighbour_id = self._get_next_nearest_neighbour_id()
        process = WriteMemoryFloodProcess(self._scamp_connection_selector)
        if isinstance(data, AbstractDataReader):
            process.write_memory_from_reader(
                nearest_neighbour_id, base_address, data, n_bytes)
        elif isinstance(data, str) and is_filename:
            reader = FileDataReader(data)
            if n_bytes is None:
                n_bytes = os.stat(data).st_size
            process.write_memory_from_reader(
                nearest_neighbour_id, base_address, reader, n_bytes)
            reader.close()
        elif isinstance(data, int):
            data_to_write = struct.pack("<I", data)
            process.write_memory_from_bytearray(
                nearest_neighbour_id, base_address, data_to_write, 0, 4)
        elif isinstance(data, long):
            data_to_write = struct.pack("<Q", data)
            process.write_memory_from_bytearray(
                nearest_neighbour_id, base_address, data_to_write, 0, 8)
        else:
            if n_bytes is None:
                n_bytes = len(data)
            process.write_memory_from_bytearray(
                nearest_neighbour_id, base_address, data, offset, n_bytes)

        # Release the lock to allow others to proceed
        self._flood_write_lock.release()

    def read_memory(self, x, y, base_address, length, cpu=0):
        """ Read some areas of SDRAM from the board

        :param x: The x-coordinate of the chip where the memory is to be\
                    read from
        :type x: int
        :param y: The y-coordinate of the chip where the memory is to be\
                    read from
        :type y: int
        :param base_address: The address in SDRAM where the region of memory\
                    to be read starts
        :type base_address: int
        :param length: The length of the data to be read in bytes
        :type length: int
        :param cpu: the core id used to read the memory of
        :type cpu: int
        :return: A bytearray of data read
        :rtype: bytearray
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    communicating with the board
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If a packet\
                    is received that is not in the valid format
        :raise spinnman.exceptions.SpinnmanInvalidParameterException:
                    * If one of x, y, p, base_address or length is invalid
                    * If a packet is received that has invalid parameters
        :raise spinnman.exceptions.SpinnmanUnexpectedResponseCodeException: If\
                    a response indicates an error during the exchange
        """

        process = ReadMemoryProcess(self._scamp_connection_selector)
        return process.read_memory(x, y, cpu, base_address, length)

    def read_neighbour_memory(self, x, y, link, base_address, length, cpu=0):
        """ Read some areas of memory on a neighbouring chip using a LINK_READ
            SCP command. If sent to a BMP, this command can be used to\
            communicate with the FPGAs' debug registers.

        :param x: The x-coordinate of the chip whose neighbour is to be\
                    read from
        :type x: int
        :param y: The y-coordinate of the chip whose neighbour is to be\
                    read from
        :type y: int
        :param cpu: The cpu to use, typically 0 (or if a BMP, the slot number)
        :type cpu: int
        :param link: The link index to send the request to (or if BMP, the\
                    FPGA number)
        :type link: int
        :param base_address: The address in SDRAM where the region of memory\
                    to be read starts
        :type base_address: int
        :param length: The length of the data to be read in bytes
        :type length: int
        :return: An iterable of chunks of data read in order
        :rtype: iterable of bytearray
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    communicating with the board
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If a packet\
                    is received that is not in the valid format
        :raise spinnman.exceptions.SpinnmanInvalidParameterException:
                    * If one of x, y, p, base_address or length is invalid
                    * If a packet is received that has invalid parameters
        :raise spinnman.exceptions.SpinnmanUnexpectedResponseCodeException: If\
                    a response indicates an error during the exchange
        """

        process = ReadMemoryProcess(self._scamp_connection_selector)
        return process.read_link_memory(x, y, cpu, link, base_address, length)

    def stop_application(self, app_id):
        """ Sends a stop request for an app_id

        :param app_id: The id of the application to send to
        :type app_id: int
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    communicating with the board
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If a packet\
                    is received that is not in the valid format
        :raise spinnman.exceptions.SpinnmanInvalidParameterException:
                    * If app_id is not a valid application id
                    * If a packet is received that has invalid parameters
        :raise spinnman.exceptions.SpinnmanUnexpectedResponseCodeException: If\
                    a response indicates an error during the exchange
        """

        if not self._machine_off:
            process = SendSingleCommandProcess(self._scamp_connection_selector)
            process.execute(AppStop(app_id))
        else:
            logger.warn(
                "You are calling a app stop on a turned off machine. "
                "Please fix and try again")

    def wait_for_cores_to_be_in_state(
            self, all_core_subsets, app_id, cpu_states, timeout=None,
            time_between_polls=0.1,
            error_states={CPUState.RUN_TIME_EXCEPTION, CPUState.WATCHDOG},
            counts_between_full_check=100):
        """

        :param all_core_subsets: the cores to check are in a given sync state
        :param app_id: the app id that being used by the simulation
        :param cpu_states:\
            The expected states once the applications are ready; success is\
            when each application is in one of these states
        :param timeout:\
            The amount of time to wait in seconds for the cores to reach one\
            of the states
        :param time_between_polls: Time between checking the state
        :param error_states:\
            Set of states that the application can be in that indicate an\
            error, and so should raise an exception
        :param counts_between_full_check:\
            The number of times to use the count signal before instead using\
            the full CPU state check
        """

        # check that the right number of processors are in the states
        processors_ready = 0
        timeout_time = None
        if timeout is not None:
            timeout_time = time.time() + timeout
        tries = 0
        while (processors_ready < len(all_core_subsets) and
               (timeout_time is None or time.time() < timeout_time)):

            # Get the number of processors in the ready states
            processors_ready = 0
            for cpu_state in cpu_states:
                processors_ready += self.get_core_state_count(
                    app_id, cpu_state)

            # If the count is too small, check for error states
            if processors_ready < len(all_core_subsets):
                for cpu_state in error_states:
                    error_cores = self.get_core_state_count(
                        app_id, cpu_state)
                    if error_cores > 0:
                        raise SpinnmanException(
                            "{} cores have reached an error state {}:".format(
                                error_cores, cpu_state))

                # If we haven't seen an error, increase the tries, and
                # do a full check if required
                tries += 1
                if tries >= counts_between_full_check:
                    cores_in_state = self.get_cores_in_state(
                        all_core_subsets, cpu_states)
                    processors_ready = len(cores_in_state)
                    tries = 0

                # If we're still not in the correct state, wait a bit
                if processors_ready < len(all_core_subsets):
                    time.sleep(time_between_polls)

        # If we haven't reached the final state, do a final full check
        if processors_ready != len(all_core_subsets):
            cores_in_state = self.get_cores_in_state(
                all_core_subsets, cpu_states)

            # If we are sure we haven't reached the final state,
            # report a timeout error
            if len(cores_in_state) != len(all_core_subsets):
                raise SpinnmanTimeoutException(
                    "waiting for cores to reach one of {}".format(cpu_states),
                    timeout)

    def get_cores_in_state(self, all_core_subsets, states):
        """ Get all cores that are in a given state or set of states

        :param all_core_subsets: The cores to filter
        :type all_core_subsets:\
                    :py:class:`spinn_machine.CoreSubsets`
        :param states: The state or states to filter on
        :type states:\
                    :py:class:`spinnman.model.enums.cpu_state.CPUState` or\
                    set of :py:class:`spinnman.model.enums.cpu_state.CPUState`
        :return: Core subsets object containing cores in the
        """
        core_infos = self.get_cpu_information(all_core_subsets)
        cores_in_state = CoreSubsets()
        for core_info in core_infos:
            if hasattr(states, "__iter__"):
                if core_info.state in states:
                    cores_in_state.add_processor(
                        core_info.x, core_info.y, core_info.p)
            elif core_info.state == states:
                cores_in_state.add_processor(
                    core_info.x, core_info.y, core_info.p)

        return cores_in_state

    def get_cores_not_in_state(self, all_core_subsets, states):
        """ Get all cores that are not in a given state or set of states

        :param all_core_subsets:
        :param states:
        :return:
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

        :param cpu_infos: A CPUInfos objects
        :type cpu_infos: :py:class:`spinnman.model.cpu_infos.CPUInfos`
        """
        break_down = "\n"
        for ((x, y, p), core_info) in cpu_infos.cpu_infos:
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

        :param app_id: The id of the application to send to
        :type app_id: int
        :param signal: The signal to send
        :type signal: :py:class:`spinnman.messages.scp.Signal`
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    communicating with the board
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If a packet\
                    is received that is not in the valid format
        :raise spinnman.exceptions.SpinnmanInvalidParameterException:
                    * If signal is not a valid signal
                    * If app_id is not a valid application id
                    * If a packet is received that has invalid parameters
        :raise spinnman.exceptions.SpinnmanUnexpectedResponseCodeException: If\
                    a response indicates an error during the exchange
        """
        process = SendSingleCommandProcess(self._scamp_connection_selector)
        process.execute(SendSignal(app_id, signal))

    def set_leds(self, x, y, cpu, led_states):
        """ Set SetLED states.

        :param x: The x-coordinate of the chip on which to set the LEDs
        :type x: int
        :param y: The x-coordinate of the chip on which to set the LEDs
        :type y: int
        :param cpu: The CPU of the chip on which to set the LEDs
        :type cpu: int
        :param led_states: A dictionary mapping SetLED index to state with\
                           0 being off, 1 on and 2 inverted.
        :type led_states: dict
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    communicating with the board
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If a packet\
                    is received that is not in the valid format
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If a\
                    packet is received that has invalid parameters
        :raise spinnman.exceptions.SpinnmanUnexpectedResponseCodeException: If\
                    a response indicates an error during the exchange
        """
        process = SendSingleCommandProcess(self._scamp_connection_selector)

        process.execute(SetLED(x, y, cpu, led_states))

    def locate_spinnaker_connection_for_board_address(self, board_address):
        """ Find a connection that matches the given board IP address

        :param board_address: The IP address of the Ethernet connection on the\
                    board
        :type board_address: str
        :return: A connection for the given IP address, or None if no such\
                    connection exists
        :rtype:\
                    :py:class:`spinnman.connections.udp_packet_connections.udp_scamp_connection.SCAMPConnection`
        """
        if board_address in self._udp_scamp_connections:
            return self._udp_scamp_connections[board_address]
        return None

    def set_ip_tag(self, ip_tag):
        """ Set up an ip tag

        :param ip_tag: The tag to set up; note board_address can be None, in\
                    which case, the tag will be assigned to all boards
        :type ip_tag: :py:class:`spinn_machine.tags.IPTag`
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    communicating with the board
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If a packet\
                    is received that is not in the valid format
        :raise spinnman.exceptions.SpinnmanInvalidParameterException:
                    * If the ip tag fields are incorrect
                    * If a packet is received that has invalid parameters
        :raise spinnman.exceptions.SpinnmanUnexpectedResponseCodeException: If\
                    a response indicates an error during the exchange
        """

        # Check that the tag has a port assigned
        if ip_tag.port is None:
            raise SpinnmanInvalidParameterException(
                "ip_tag.port", "None",
                "The tag port must have been set")

        # Get the connections - if the tag specifies a connection, use that,
        # otherwise apply the tag to all connections
        connections = list()
        if ip_tag.board_address is not None:
            connection = self.locate_spinnaker_connection_for_board_address(
                ip_tag.board_address)
            if connection is None:
                raise SpinnmanInvalidParameterException(
                    "ip_tag", str(ip_tag),
                    "The given board address is not recognised")
            connections.append(connection)
        else:
            connections = self._scamp_connections

        for connection in connections:

            # Convert the host string
            host_string = ip_tag.ip_address
            if (host_string == "localhost" or host_string == "." or
                    host_string == "0.0.0.0"):
                host_string = connection.local_ip_address
            ip_string = socket.gethostbyname(host_string)
            ip_address = bytearray(socket.inet_aton(ip_string))

            process = SendSingleCommandProcess(self._scamp_connection_selector)
            process.execute(IPTagSet(
                connection.chip_x, connection.chip_y, ip_address, ip_tag.port,
                ip_tag.tag, strip=ip_tag.strip_sdp))

    def set_reverse_ip_tag(self, reverse_ip_tag):
        """ Set up a reverse ip tag

        :param reverse_ip_tag: The reverse tag to set up; note board_address\
                    can be None, in which case, the tag will be assigned to\
                    all boards
        :type reverse_ip_tag:\
                    :py:class:`spinn_machine.tags.ReverseIPTag`
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    communicating with the board
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If a packet\
                    is received that is not in the valid format
        :raise spinnman.exceptions.SpinnmanInvalidParameterException:
                    * If the reverse ip tag fields are incorrect
                    * If a packet is received that has invalid parameters
                    * If the UDP port is one that is already used by\
                      spiNNaker for system functions
        :raise spinnman.exceptions.SpinnmanUnexpectedResponseCodeException: If\
                    a response indicates an error during the exchange
        """

        if reverse_ip_tag.port is None:
            raise SpinnmanInvalidParameterException(
                "reverse_ip_tag.port", "None",
                "The tag port must have been set!")

        if (reverse_ip_tag.port == constants.SCP_SCAMP_PORT or
                reverse_ip_tag.port ==
                constants.UDP_BOOT_CONNECTION_DEFAULT_PORT):
            raise SpinnmanInvalidParameterException(
                "reverse_ip_tag.port", reverse_ip_tag.port,
                "The port number for the reverse ip tag conflicts with"
                " the spiNNaker system ports ({} and {})".format(
                    constants.SCP_SCAMP_PORT,
                    constants.UDP_BOOT_CONNECTION_DEFAULT_PORT))

        # Get the connections - if the tag specifies a connection, use that,
        # otherwise apply the tag to all connections
        connections = list()
        if reverse_ip_tag.board_address is not None:
            connection = self.locate_spinnaker_connection_for_board_address(
                reverse_ip_tag.board_address)
            if connection is None:
                raise SpinnmanInvalidParameterException(
                    "reverse_ip_tag", str(reverse_ip_tag),
                    "The given board address is not recognised")
            connections.append(connection)
        else:
            connections = self._scamp_connections

        for connection in connections:
            process = SendSingleCommandProcess(self._scamp_connection_selector)
            process.execute(ReverseIPTagSet(
                connection.chip_x, connection.chip_y,
                reverse_ip_tag.destination_x, reverse_ip_tag.destination_y,
                reverse_ip_tag.destination_p,
                reverse_ip_tag.port, reverse_ip_tag.tag,
                reverse_ip_tag.sdp_port))

    def clear_ip_tag(self, tag, connection=None, board_address=None):
        """ Clear the setting of an ip tag

        :param tag: The tag id
        :type tag: int
        :param connection: Connection where the tag should be cleared.  If not\
                    specified, all SCPSender connections will send the message\
                    to clear the tag
        :type connection:\
                    :py:class:`spinnman.connections.abstract_classes.SCPSender`
        :param board_address: Board address where the tag should be cleared.\
                    If not specified, all SCPSender connections will send the\
                    message to clear the tag
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    communicating with the board
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If a packet\
                    is received that is not in the valid format
        :raise spinnman.exceptions.SpinnmanInvalidParameterException:
                    * If the tag is not a valid tag
                    * If the connection cannot send SDP messages
                    * If a packet is received that has invalid parameters
        :raise spinnman.exceptions.SpinnmanUnexpectedResponseCodeException: If\
                    a response indicates an error during the exchange
        """
        if connection is not None:
            connections = [connection]
        elif board_address is not None:
            connection = self.locate_spinnaker_connection_for_board_address(
                board_address)
            connections = [connection]
        else:
            connections = self._scamp_connections

        for connection in connections:
            process = SendSingleCommandProcess(self._scamp_connection_selector)
            process.execute(IPTagClear(
                connection.chip_x, connection.chip_y, tag))

    def get_tags(self, connection=None):
        """ Get the current set of tags that have been set on the board

        :param connection: Connection from which the tags should be received.\
                    If not specified, all SCPSender connections will be\
                    queried and the response will be combined.
        :type connection:\
                    :py:class:`spinnman.connections.abstract_classes.SCPSender`
        :return: An iterable of tags
        :rtype: iterable of\
                    :py:class:`spinn_machine.tags.AbstractTag`
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    communicating with the board
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If a packet\
                    is received that is not in the valid format
        :raise spinnman.exceptions.SpinnmanInvalidParameterException:
                    * If the connection cannot send SDP messages
                    * If a packet is received that has invalid parameters
        :raise spinnman.exceptions.SpinnmanUnexpectedResponseCodeException: If\
                    a response indicates an error during the exchange
        """
        if connection is not None:
            connections = connection
        else:
            connections = self._scamp_connections

        all_tags = list()
        for connection in connections:
            process = GetTagsProcess(self._scamp_connection_selector)
            all_tags.extend(process.get_tags(connection))
        return all_tags

    def malloc_sdram(self, x, y, size, app_id, tag=None):
        """ Allocates a chunk of SDRAM on a chip on the machine

        :param x: The x-coordinate of the chip onto which to ask for memory
        :type x: int
        :param y: The y-coordinate of the chip onto which to ask for memory
        :type y: int
        :param size: the amount of memory to allocate in bytes
        :type size: int
        :param app_id: The id of the application with which to associate the\
                    routes.  If not specified, defaults to 0.
        :type app_id: int
        :param tag: the tag for the SDRAM, a 8-bit (chip-wide) tag that can be\
                    looked up by a SpiNNaker application to discover the\
                    address of the allocated block. If `0` then no tag is\
                    applied.
        :type tag: int
        :return: the base address of the allocated memory
        :rtype: int
        """
        process = MallocSDRAMProcess(self._scamp_connection_selector)
        process.malloc_sdram(x, y, size, app_id, tag)
        return process.base_address

    def free_sdram(self, x, y, base_address, app_id):
        """ Free allocated SDRAM

        :param x: The x-coordinate of the chip onto which to ask for memory
        :type x: int
        :param y: The y-coordinate of the chip onto which to ask for memory
        :type y: int
        :param base_address: The base address of the allocated memory
        :type base_address: int
        :param app_id: The app id of the allocated memory
        :type app_id: int
        """
        process = DeAllocSDRAMProcess(self._scamp_connection_selector)
        process.de_alloc_sdram(x, y, app_id, base_address)

    def free_sdram_by_app_id(self, x, y, app_id):
        """ Free all SDRAM allocated to a given app id

        :param x: The x-coordinate of the chip onto which to ask for memory
        :type x: int
        :param y: The y-coordinate of the chip onto which to ask for memory
        :type y: int
        :param app_id: The app id of the allocated memory
        :type app_id: int
        :return: The number of blocks freed
        :rtype: int
        """
        process = DeAllocSDRAMProcess(self._scamp_connection_selector)
        process.de_alloc_sdram(x, y, app_id)
        return process.no_blocks_freed

    def load_multicast_routes(self, x, y, routes, app_id):
        """ Load a set of multicast routes on to a chip

        :param x: The x-coordinate of the chip onto which to load the routes
        :type x: int
        :param y: The y-coordinate of the chip onto which to load the routes
        :type y: int
        :param routes: An iterable of multicast routes to load
        :type routes: iterable of\
                    :py:class:`spinn_machine.MulticastRoutingEntry`
        :param app_id: The id of the application with which to associate the\
                    routes.  If not specified, defaults to 0.
        :type app_id: int
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    communicating with the board
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If a packet\
                    is received that is not in the valid format
        :raise spinnman.exceptions.SpinnmanInvalidParameterException:
                    * If any of the routes are invalid
                    * If a packet is received that has invalid parameters
        :raise spinnman.exceptions.SpinnmanUnexpectedResponseCodeException: If\
                    a response indicates an error during the exchange
        """

        process = LoadMultiCastRoutesProcess(self._scamp_connection_selector)

        process.load_routes(x, y, routes, app_id)

    def get_multicast_routes(self, x, y, app_id=None):
        """ Get the current multicast routes set up on a chip

        :param x: The x-coordinate of the chip from which to get the routes
        :type x: int
        :param y: The y-coordinate of the chip from which to get the routes
        :type y: int
        :param app_id: The id of the application to filter the routes for.  If\
                    not specified, will return all routes
        :type app_id: int
        :return: An iterable of multicast routes
        :rtype: iterable of\
                    :py:class:`spinnman.model.multicast_routing_entry.MulticastRoute`
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    communicating with the board
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If a packet\
                    is received that is not in the valid format
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If a\
                    packet is received that has invalid parameters
        :raise spinnman.exceptions.SpinnmanUnexpectedResponseCodeException: If\
                    a response indicates an error during the exchange
        """
        base_address = self._get_sv_data(
            x, y, SystemVariableDefinition.router_table_copy_address)
        process = GetMultiCastRoutesProcess(
            self._scamp_connection_selector, app_id)
        return process.get_routes(x, y, base_address)

    def clear_multicast_routes(self, x, y):
        """ Remove all the multicast routes on a chip

        :param x: The x-coordinate of the chip on which to clear the routes
        :type x: int
        :param y: The y-coordinate of the chip on which to clear the routes
        :type y: int
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    communicating with the board
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If a packet\
                    is received that is not in the valid format
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If a\
                    packet is received that has invalid parameters
        :raise spinnman.exceptions.SpinnmanUnexpectedResponseCodeException: If\
                    a response indicates an error during the exchange
        """
        process = SendSingleCommandProcess(self._scamp_connection_selector)
        process.execute(RouterClear(x, y))

    def get_router_diagnostics(self, x, y):
        """ Get router diagnostic information from a chip

        :param x: The x-coordinate of the chip from which to get the\
                    information
        :type x: int
        :param y: The y-coordinate of the chip from which to get the\
                    information
        :type y: int
        :return: The router diagnostic information
        :rtype: :py:class:`spinnman.model.router_diagnostics.RouterDiagnostics`
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    communicating with the board
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If a packet\
                    is received that is not in the valid format
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If a\
                    packet is received that has invalid parameters
        :raise spinnman.exceptions.SpinnmanUnexpectedResponseCodeException: If\
                    a response indicates an error during the exchange
        """
        process = ReadRouterDiagnosticsProcess(self._scamp_connection_selector)
        return process.get_router_diagnostics(x, y)

    def set_router_diagnostic_filter(self, x, y, position, diagnostic_filter):
        """ Sets a router diagnostic filter in a router

        :param x: the x address of the router in which this filter is being\
                    set
        :type x: int
        :param y: the y address of the router in which this filter is being\
                    set
        :type y: int
        :param position: the position in the list of filters where this filter\
                    is to be added
        :type position: int
        :param diagnostic_filter: the diagnostic filter being set in the\
                    placed, between 0 and 15 (note that positions 0 to 11 are\
                    used by the default filters, and setting these positions\
                    will result in a warning).
        :type diagnostic_filter:\
                    :py:class:`spinnman.model.diagnostic_filter.DiagnosticFilter`
        :rtype: None
        :raise spinnman.exceptions.SpinnmanIOException:
                    * If there is an error communicating with the board
                    * If there is an error reading the data
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If a packet\
                    is received that is not in the valid format
        :raise spinnman.exceptions.SpinnmanInvalidParameterException:
                    * If x, y does not lead to a valid chip
                    * If position is less than 0 or more than 15
        :raise spinnman.exceptions.SpinnmanUnexpectedResponseCodeException: If\
                    a response indicates an error during the exchange
        """
        data_to_send = diagnostic_filter.filter_word
        if position > constants.NO_ROUTER_DIAGNOSTIC_FILTERS:
            raise SpinnmanInvalidParameterException(
                "position", str(position), "the range of the position of a "
                                           "router filter is 0 and 16.")
        if position <= constants.ROUTER_DEFAULT_FILTERS_MAX_POSITION:
            logger.warn(
                " You are planning to change a filter which is set by default."
                " By doing this, other runs occurring on this machine will be "
                "forced to use this new configuration until the machine is "
                "reset. Please also note that these changes will make the"
                " the reports from ybug not correct."
                "This has been executed and is trusted that the end user knows"
                " what they are doing")
        memory_position = (constants.ROUTER_REGISTER_BASE_ADDRESS +
                           constants.ROUTER_FILTER_CONTROLS_OFFSET +
                           (position *
                            constants.ROUTER_DIAGNOSTIC_FILTER_SIZE))

        process = SendSingleCommandProcess(self._scamp_connection_selector)
        process.execute(WriteMemory(
            x, y, memory_position, struct.pack("<I", data_to_send)))

    def get_router_diagnostic_filter(self, x, y, position):
        """ Gets a router diagnostic filter from a router

        :param x: the x address of the router from which this filter is being\
                    retrieved
        :type x: int
        :param y: the y address of the router from which this filter is being\
                    retrieved
        :type y: int
        :param position: the position in the list of filters where this filter\
                    is to be added
        :type position: int
        :return: The diagnostic filter read
        :rtype: :py:class:`spinnman.model.diagnostic_filter.DiagnosticFilter`
        :raise spinnman.exceptions.SpinnmanIOException:
                    * If there is an error communicating with the board
                    * If there is an error reading the data
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If a packet\
                    is received that is not in the valid format
        :raise spinnman.exceptions.SpinnmanInvalidParameterException:
                    * If x, y does not lead to a valid chip
                    * If a packet is received that has invalid parameters
                    * If position is less than 0 or more than 15
        :raise spinnman.exceptions.SpinnmanUnexpectedResponseCodeException: If\
                    a response indicates an error during the exchange
        """
        memory_position = (constants.ROUTER_REGISTER_BASE_ADDRESS +
                           constants.ROUTER_FILTER_CONTROLS_OFFSET +
                           (position *
                            constants.ROUTER_DIAGNOSTIC_FILTER_SIZE))
        process = SendSingleCommandProcess(self._scamp_connection_selector)
        response = process.execute(
            ReadMemory(x, y, memory_position, 4))
        return DiagnosticFilter.read_from_int(struct.unpack_from(
            "<I", response.data, response.offset)[0])

    def clear_router_diagnostic_counters(self, x, y, enable=True,
                                         counter_ids=range(0, 16)):
        """ Clear router diagnostic information on a chip

        :param x: The x-coordinate of the chip
        :type x: int
        :param y: The y-coordinate of the chip
        :type y: int
        :param enable: True (default) if the counters should be enabled
        :type enable: bool
        :param counter_ids: The ids of the counters to reset (all by default)\
                    and enable if enable is True; each must be between 0 and 15
        :type counter_ids: array-like of int
        :rtype: None
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    communicating with the board
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If a packet\
                    is received that is not in the valid format
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If a\
                    packet is received that has invalid parameters or a\
                    counter id is out of range
        :raise spinnman.exceptions.SpinnmanUnexpectedResponseCodeException: If\
                    a response indicates an error during the exchange
        """
        clear_data = 0
        for counter_id in counter_ids:
            if counter_id < 0 or counter_id > 15:
                raise SpinnmanInvalidParameterException(
                    "counter_id", counter_id,
                    "Diagnostic counter ids must be between 0 and 15")
            clear_data |= 1 << counter_id
        if enable:
            for counter_id in counter_ids:
                clear_data |= 1 << counter_id + 16
        process = SendSingleCommandProcess(self._scamp_connection_selector)
        process.execute(WriteMemory(
            x, y, 0xf100002c, struct.pack("<I", clear_data)))

    @property
    def number_of_boards_located(self):
        """ Get the number of boards currently configured
        """
        boards = 0
        for bmp_connection in self._bmp_connections:
            boards += len(bmp_connection.boards)

        # if no BMPs are available, then there's still at least one board
        if boards == 0:
            boards = 1
        return boards

    def close(self, close_original_connections=True, power_off_machine=False):
        """ Close the transceiver and any threads that are running

        :param close_original_connections: If True, the original connections\
                    passed to the transceiver in the constructor are also\
                    closed.  If False, only newly discovered connections are\
                    closed.
        :param power_off_machine: if true, the machine is sent a power down\
                    command via its BMP (if it has one)
        :type power_off_machine: bool
        :return: Nothing is returned
        :rtype: None
        :raise None: No known exceptions are raised
        """

        if self._reinjection_running:
            process = ExitDPRIProcess(self._scamp_connection_selector)
            process.exit(self._reinjector_cores)
            self.stop_application(self._reinjector_app_id)
            self._reinjection_running = False

        if power_off_machine and len(self._bmp_connections) > 0:
            self.power_off_machine()

        for receiving_connections in \
                self._udp_receive_connections_by_port.values():
            for (_, listener) in receiving_connections.values():
                if listener is not None:
                    listener.close()

        for connection in self._all_connections:
            if (close_original_connections or
                    connection not in self._original_connections):
                connection.close()

    def register_udp_listener(self, callback, connection_class,
                              local_port=None, local_host=None):
        """ Register a callback for a certain type of traffic to be received\
            via UDP.  Note that the connection class must extend\
            :py:class:`spinnman.connections.abstract_classes.Listenable`
            to avoid clashing with the SCAMP and BMP functionality

        :param callback: Function to be called when a packet is received
        :type callback: function(packet)
        :param connection_class: The class of connection to receive using
        :param local_port: The optional port number to listen on; if not\
                specified, an existing connection will be used if possible,\
                otherwise a random free port number will be used
        :type local_port: int
        :param local_host: The optional hostname or IP address to listen on;\
                if not specified, all interfaces will be used for listening
        :type local_host: str
        :return: The connection to be used
        :rtype:\
                :py:class:`spinnman.connection.udp_packet_connections.UDPConnection`
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
            if len(receiving_connections) > 0:

                if local_host is None or local_host == "0.0.0.0":

                    # If we are to listen on all interfaces and the listener
                    # is not on all interfaces, this is an error
                    if "0.0.0.0" not in receiving_connections:
                        raise SpinnmanInvalidParameterException(
                            "local_port", local_port,
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
                    (connection, listener) = receiving_connections[local_host]
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
        if len(connections_of_class) > 0:

            # If local_host is not specified, normalise it
            if local_host is None:
                local_host = "0.0.0.0"

            for (a_connection, a_listener) in connections_of_class:

                # Find a connection that matches the local host
                if a_connection.local_ip_address == local_host:
                    (connection, listener) = (a_connection, a_listener)
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

    def enable_reinjection(self, multicast=True, point_to_point=False,
                           nearest_neighbour=False, fixed_route=False):
        """ Enables or disables dropped packet reinjection - if all parameters\
            are false, dropped packet reinjection will be disabled

        :param multicast: If True, multicast dropped packet reinjection is\
                enabled
        :type multicast: bool
        :param point_to_point: If True, point to point dropped packet\
                reinjection is enabled
        :type point_to_point: bool
        :param nearest_neighbour: If True, nearest_neighbour dropped packet\
                reinjection is enabled
        :type nearest_neighbour: bool
        :param fixed_route: If True, fixed route dropped packet reinjection is\
                enabled
        :type fixed_route: bool
        """
        if not self._machine_off:
            if not self._reinjection_running:

                # Get the machine
                if self._machine is None:
                    self._update_machine()

                # Find a free core on each chip to use
                if self._reinjector_cores is None:
                    self._reinjector_cores, failed_chips = \
                        self._machine.reserve_system_processors()
                    if len(failed_chips) > 0:
                        logger.warn(
                            "The reinjector could not be enabled on the "
                            "following chips due to lack of available cores: "
                            "{}".format(failed_chips))

                # Get an app id for the reinjector
                if self._reinjector_app_id is None:
                    self._reinjector_app_id = self._app_id_tracker.get_new_id()

                # Load the reinjector on each free core
                reinjector_binary = os.path.join(
                    os.path.dirname(model_binaries.__file__),
                    "reinjector.aplx")
                self.execute_flood(
                    self._reinjector_cores, reinjector_binary,
                    self._reinjector_app_id, is_filename=True)
                self.wait_for_cores_to_be_in_state(
                    self._reinjector_cores, self._reinjector_app_id,
                    [CPUState.RUNNING])
                self._reinjection_running = True

            # Set the types to be reinjected
            process = SetDPRIPacketTypesProcess(
                self._scamp_connection_selector)
            packet_types = list()
            values_to_check = [multicast, point_to_point,
                               nearest_neighbour, fixed_route]
            flags_to_set = [DPRIFlags.MULTICAST,
                            DPRIFlags.POINT_TO_POINT,
                            DPRIFlags.NEAREST_NEIGHBOUR,
                            DPRIFlags.FIXED_ROUTE]
            for value, flag in zip(values_to_check, flags_to_set):
                if value:
                    packet_types.append(flag)
            process.set_packet_types(packet_types, self._reinjector_cores)
        else:
            logger.warn("Ignoring exception in enable_reinjection as "
                        "machine if probably off")

    def set_reinjection_router_timeout(self, timeout_mantissa,
                                       timeout_exponent):
        """ Sets the timeout of the routers

        :param timeout_mantissa: The mantissa of the timeout value, between 0\
                and 15
        :type timeout_mantissa: int
        :param timeout_exponent: The exponent of the timeout value, between 0\
                and 15
        :type timeout_exponent: int
        """
        if not self._reinjection_running:
            self.enable_reinjection()
        process = SetDPRIRouterTimeoutProcess(self._scamp_connection_selector)
        process.set_timeout(timeout_mantissa, timeout_exponent,
                            self._reinjector_cores)

    def set_reinjection_router_emergency_timeout(self, timeout_mantissa,
                                                 timeout_exponent):
        """ Sets the timeout of the routers

        :param timeout_mantissa: The mantissa of the timeout value, between 0\
                and 15
        :type timeout_mantissa: int
        :param timeout_exponent: The exponent of the timeout value, between 0\
                and 15
        :type timeout_exponent: int
        """
        if not self._reinjection_running:
            self.enable_reinjection()
        process = SetDPRIRouterEmergencyTimeoutProcess(
            self._scamp_connection_selector)
        process.set_timeout(timeout_mantissa, timeout_exponent,
                            self._reinjector_cores)

    def reset_reinjection_counters(self):
        """ Resets the counters for reinjection
        """
        if not self._reinjection_running:
            self.enable_reinjection()
        process = ResetDPRICountersProcess(self._scamp_connection_selector)
        process.reset_counters(self._reinjector_cores)

    def get_reinjection_status(self, x, y):
        """ Get the status of the reinjection on a given chip

        :param x: The x-coordinate of the chip
        :type x: int
        :param y: The y-coordinate of the chip
        :type y: int
        :return: The reinjection status of the chip, or None if reinjection is\
                not enabled
        :rtype: None or :py:class:`spinnman.model.dpri_status.DPRIStatus`
        """
        if not self._reinjection_running:
            return None
        process = ReadDPRIStatusProcess(self._scamp_connection_selector)
        reinjector_core = next(
            self._reinjector_cores.get_core_subset_for_chip(x, y)
            .processor_ids)
        return process.get_dpri_status(x, y, reinjector_core)

    def __str__(self):
        return "transceiver object connected to {} with {} connections"\
            .format(self._scamp_connections[0].remote_ip_address,
                    len(self._all_connections))

    def __repr__(self):
        return self.__str__()
