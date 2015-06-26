from spinnman.connections.udp_packet_connections.iptag_connection\
    import IPTagConnection
from spinnman.model.diagnostic_filter import DiagnosticFilter
from spinnman.connections.abstract_classes.abstract_spinnaker_boot_receiver\
    import AbstractSpinnakerBootReceiver
from spinnman.connections.abstract_classes.abstract_spinnaker_boot_sender\
    import AbstractSpinnakerBootSender
from spinnman.connections.abstract_classes.abstract_udp_connection\
    import AbstractUDPConnection
from spinnman.connections.abstract_classes.abstract_scp_sender\
    import AbstractSCPSender
from spinnman.connections.abstract_classes.abstract_sdp_sender\
    import AbstractSDPSender
from spinnman.connections.abstract_classes.abstract_multicast_sender\
    import AbstractMulticastSender
from spinnman.connections.abstract_classes.abstract_scp_receiver\
    import AbstractSCPReceiver
import random
from spinnman.processes.get_machine_process import GetMachineProcess
from spinnman.processes.get_version_process import GetVersionProcess
from spinnman.processes.write_memory_process import WriteMemoryProcess
from spinnman.processes.read_memory_process import ReadMemoryProcess
from spinnman.messages.scp.impl.scp_iptag_tto_request import SCPIPTagTTORequest
from spinnman.processes.get_cpu_info_process import GetCPUInfoProcess
from spinnman.processes.read_iobuf_process import ReadIOBufProcess
from spinnman.processes.application_run_process import ApplicationRunProcess
from spinnman.processes.write_memory_flood_process import WriteMemoryFloodProcess
from spinnman.processes.get_tags_process import GetTagsProcess
from spinnman.processes.load_routes_process import LoadRoutesProcess
from spinnman.processes.get_routes_process import GetRoutesProcess
import struct
from spinnman.processes.read_router_diagnostics_process import ReadRouterDiagnosticsProcess
from spinnman.processes.send_single_command_process \
    import SendSingleCommandProcess
from spinnman.connections.udp_packet_connections.stripped_iptag_connection \
    import StrippedIPTagConnection
from spinnman.connections.udp_packet_connections.udp_boot_connection \
    import UDPBootConnection
from spinnman import constants
from spinnman.connections.udp_packet_connections.udp_spinnaker_connection \
    import UDPSpinnakerConnection
from spinnman.exceptions import SpinnmanUnsupportedOperationException
from spinnman.exceptions import SpinnmanTimeoutException
from spinnman.exceptions import SpinnmanInvalidParameterException
from spinnman.exceptions import SpinnmanIOException
from spinnman.exceptions import SpinnmanUnexpectedResponseCodeException
from spinnman.messages.scp.impl.scp_reverse_iptag_set_request import \
    SCPReverseIPTagSetRequest

from spinnman.model.machine_dimensions import MachineDimensions
from spinnman.model.core_subsets import CoreSubsets
from spinnman.model.router_diagnostics import RouterDiagnostics

from spinnman.messages.spinnaker_boot.spinnaker_boot_messages \
    import SpinnakerBootMessages
from spinnman.messages.scp.impl.scp_read_link_request \
    import SCPReadLinkRequest
from spinnman.messages.scp.impl.scp_read_memory_request \
    import SCPReadMemoryRequest
from spinnman.messages.scp.impl.scp_count_state_request \
    import SCPCountStateRequest
from spinnman.messages.scp.impl.scp_write_memory_request \
    import SCPWriteMemoryRequest
from spinnman.messages.scp.impl.scp_flood_fill_start_request \
    import SCPFloodFillStartRequest
from spinnman.messages.scp.impl.scp_flood_fill_data_request \
    import SCPFloodFillDataRequest
from spinnman.messages.scp.impl.scp_flood_fill_end_request \
    import SCPFloodFillEndRequest
from spinnman.messages.scp.impl.scp_application_run_request \
    import SCPApplicationRunRequest
from spinnman.messages.scp.impl.scp_send_signal_request \
    import SCPSendSignalRequest
from spinnman.messages.scp.impl.scp_iptag_set_request \
    import SCPIPTagSetRequest
from spinnman.messages.scp.impl.scp_iptag_clear_request \
    import SCPIPTagClearRequest
from spinnman.messages.scp.impl.scp_router_alloc_request \
    import SCPRouterAllocRequest
from spinnman.messages.scp.impl.scp_router_init_request \
    import SCPRouterInitRequest
from spinnman.messages.scp.impl.scp_router_clear_request \
    import SCPRouterClearRequest
from spinnman.messages.scp.impl.scp_led_request \
    import SCPLEDRequest
from spinnman.messages.scp.impl.scp_app_stop_request import SCPAppStopRequest
from spinnman.messages.scp.scp_result import SCPResult

from spinnman.data.abstract_data_reader import AbstractDataReader
from spinnman.data.little_endian_byte_array_byte_writer \
    import LittleEndianByteArrayByteWriter
from spinnman.data.little_endian_byte_array_byte_reader \
    import LittleEndianByteArrayByteReader

# noinspection

from spinn_machine.multicast_routing_entry import MulticastRoutingEntry

from threading import Condition
from socket import gethostbyname
from socket import inet_aton

import logging
import math


logger = logging.getLogger(__name__)

_SCAMP_NAME = "SC&MP"
_SCAMP_VERSION = 1.33


def create_transceiver_from_hostname(
        hostname, ignore_chips=None, ignore_cores=None, max_core_id=None):
    """ Create a Transceiver by creating a UDPConnection to the given\
        hostname on port 17893 (the default SCAMP port), and a\
        UDPBootConnection on port 54321 (the default boot port),
        optionally discovering any additional links using the UDPConnection,\
        and then returning the transceiver created with the conjunction of the\
        created UDPConnection and the discovered connections

    :param hostname: The hostname or IP address of the board
    :type hostname: str
    :param ignore_chips: An optional set of chips to ignore in the\
                machine.  Requests for a "machine" will have these chips\
                excluded, as if they never existed.  The processor_ids of\
                the specified chips are ignored.
    :type ignore_chips: :py:class:`spinnman.model.core_subsets.CoreSubsets`
    :param ignore_cores: An optional set of cores to ignore in the\
                machine.  Requests for a "machine" will have these cores\
                excluded, as if they never existed.
    :type ignore_cores: :py:class:`spinnman.model.core_subsets.CoreSubsets`
    :param max_core_id: The maximum core id in any discovered machine.\
                Requests for a "machine" will only have core ids up to\
                this value.
    :type max_core_id: int
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
    connection = UDPSpinnakerConnection(remote_host=hostname)
    boot_connection = UDPBootConnection(remote_host=hostname)
    return Transceiver(
        connections=[connection, boot_connection], ignore_chips=ignore_chips,
        ignore_cores=ignore_cores, max_core_id=max_core_id)


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

    def __init__(self, connections=None, ignore_chips=None,
                 ignore_cores=None, max_core_id=None):
        """

        :param connections: An iterable of connections to the board.  If not\
                    specified, no communication will be possible until\
                    connections are found.
        :type connections: iterable of\
                    :py:class:`spinnman.connections.abstract_connection.AbstractConnection`
        :param ignore_chips: An optional set of chips to ignore in the\
                    machine.  Requests for a "machine" will have these chips\
                    excluded, as if they never existed.  The processor_ids of\
                    the specified chips are ignored.
        :type ignore_chips: :py:class:`spinnman.model.core_subsets.CoreSubsets`
        :param ignore_cores: An optional set of cores to ignore in the\
                    machine.  Requests for a "machine" will have these cores\
                    excluded, as if they never existed.
        :type ignore_cores: :py:class:`spinnman.model.core_subsets.CoreSubsets`
        :param max_core_id: The maximum core id in any discovered machine.\
                    Requests for a "machine" will only have core ids up to and\
                    including this value.
        :type max_core_id: int
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
        self._machine = None
        self._ignore_chips = ignore_chips
        self._ignore_cores = ignore_cores
        self._max_core_id = max_core_id

        # Place to keep the known chip information
        self._chip_info = dict()

        # A set of the original connections - used to determine what can
        # be closed
        self._original_connections = set()
        if connections is not None:
            self._original_connections.update(connections)

        # A set of all connection - used for closing
        self._all_connections = set()
        if connections is not None:
            self._all_connections.update(connections)

        # A boot send connection - there can only be one in the current system,
        # or otherwise bad things can happen!
        self._boot_send_connection = None

        # A list of boot receive connections - these are used to
        # listen for the pre-boot board identifiers
        self._boot_receive_connections = list()

        # A dict of (ip address, port) -> connection for udp connections
        # Used to keep track of what connection is listening on what port
        # to ensure only one type of traffic is received on any port for any
        # interface
        self._udp_receive_connections = dict()

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

    def _sort_out_connections(self, connections):

        for connection in connections:

            # locate the only boot send connection
            if isinstance(connection, AbstractSpinnakerBootSender):
                if self._boot_send_connection is not None:
                    raise SpinnmanInvalidParameterException(
                        "connections", "[... {} ...]".format(connection),
                        "Only a single AbstractSpinnakerBootSender can be"
                        " specified")
                else:
                    self._boot_send_connection = connection

            # locate any boot receiver connections
            if isinstance(connection, AbstractSpinnakerBootReceiver):
                self._boot_receive_connections.append(connection)

            # Locate any connections listening on a UDP port
            if isinstance(connection, AbstractUDPConnection):
                self._udp_receive_connections[
                    (connection.local_ip_address,
                     connection.local_port)] = connection

            # Locate any connections that can send SCP
            if isinstance(connection, AbstractSCPSender):
                self._scp_sender_connections.append(connection)

            # Locate any connections that can send SDP
            if isinstance(connection, AbstractSDPSender):
                self._sdp_sender_connections.append(connection)

            # Locate any connections that can send Multicast
            if isinstance(connection, AbstractMulticastSender):
                self._multicast_sender_connections.append(connection)

            # Locate any connections that can send and receive SCP
            if (isinstance(connection, AbstractSCPSender) and
                    isinstance(connection, AbstractSCPReceiver)):

                self._scamp_connections.append(connection)

                # If also a UDP connection, add it here (for IP tags)
                if isinstance(connection, AbstractUDPConnection):
                    board_address = connection.remote_ip_address
                    self._udp_scamp_connections[board_address] = connection

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

    def _find_best_scamp_connection(self, x, y):
        """ Finds the best connection queue to use to perform a scamp operation

        :param x: The x-coordinate of the chip that the message is going to
        :type x: int
        :param y: The y-coordinate of the chip that the message is going to
        :type y: int
        :return: The best connection to use
        :rtype:\
                    :py:class:`spinnman.connections.abstract_classes.abstract_connection.AbstractConnection`
        :raise spinnman.exceptions.SpinnmanUnsupportedOperationException: If\
                    no connection is available
        """

        # TODO: Do something better than this
        return self._scamp_connections[0]

    def _get_random_connection(self, connections, connection=None):
        """ Returns the given connection, or else picks one at random
        """
        if connection is not None:
            return connection
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
                    :py:class:`spinnman.connections.abstract_connection.AbstractConnection`
        :return: The received response, or the callback if get_callback is True
        :rtype:\
                    :py:class:`spinnman.messages.scp.abstract_scp_response.AbstractSCPResponse`
        :raise spinnman.exceptions.SpinnmanTimeoutException: If there is a\
                    timeout before a message is received
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If one\
                    of the fields of the received message is invalid
        :raise spinnman.exceptions.SpinnmanInvalidPacketException:
                    * If the message is not a recognized packet type
                    * If a packet is received that is not a valid response
        :raise spinnman.exceptions.SpinnmanUnsupportedOperationException: If\
                    no connection can send the type of message given
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    sending the message or receiving the response
        :raise spinnman.exceptions.SpinnmanUnexpectedResponseCodeException: If\
                    the response is not one of the expected codes
        """
        connection_to_use = self._get_random_connection(
            self._scp_sender_connections, connection)
        connection_to_use.send_scp_request(message)

    def send_sdp_message(self, message, connection=None):
        """ Sends an SDP message using one of the connections.

        :param message: The message to send
        :type message: SDPMessage
        :param connection: An optional connection to use
        :type connection:\
                    :py:class:`spinnman.connections.abstract_connection.AbstractConnection`
        :return: None
        """
        connection_to_use = self._get_random_connection(
            self._sdp_sender_connections, connection)
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
                    :py:class:`spinnman.connections.abstract_multicast_sender.AbstractMulticastSender`
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

        # Get the details of all the chips
        get_machine_process = GetMachineProcess(
            self._scamp_connections, self._ignore_chips, self._ignore_cores,
            self._max_core_id)
        self._machine = get_machine_process.get_machine_details()
        self._chip_info = get_machine_process.get_chip_info()
        logger.info(self._machine.cores_and_link_output_string())

    def discover_scamp_connections(self):
        """ Find connections to the board and store these for future use.\
            Note that connections can be empty, in which case another local\
            discovery mechanism will be used.  Note that an exception will be\
            thrown if no initial connections can be found to the board.

        :return: An iterable of discovered connections, not including the\
                    initially given connections in the constructor
        :rtype: iterable of\
                    :py:class:`spinnman.connections.abstract_connection.AbstractConnection`
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
        if len(self._udp_scamp_connections) == 0:
            return list()
        self._update_machine()

        # Find all the new connections via the machine ethernet-connected chips
        new_connections = list()
        for chip in self._machine.ethernet_connected_chips:
            if chip.ip_address not in self._udp_scamp_connections:
                new_connection = UDPSpinnakerConnection(
                    remote_host=chip.ip_address, chip_x=chip.x, chip_y=chip.y)
                new_connections.append(new_connection)
                self._udp_scamp_connections[chip.ip_address] = new_connection
                self._scamp_connections.append(new_connection)
                self._scp_sender_connections.append(new_connection)
                self._all_connections.add(new_connection)

        # Update the connection queues after finding new connections
        return new_connections

    def get_connections(self, include_boot_connection=False):
        """ Get the currently known connections to the board, made up of those\
            passed in to the transceiver and those that are discovered during\
            calls to discover_connections.  No further discovery is done here.

        :param include_boot_connection: this parameter signals if the returned\
               list of connections should include also the boot connection to\
               SpiNNaker
        :type include_boot_connection: bool
        :return: An iterable of connections known to the transceiver
        :rtype: iterable of\
                    :py:class:`spinnman.connections.abstract_connection.AbstractConnection`
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
        if self._machine is None:
            self._update_machine()
        return MachineDimensions(self._machine.max_chip_x,
                                 self._machine.max_chip_y)

    def get_machine_details(self):
        """ Get the details of the machine made up of chips on a board and how\
            they are connected to each other.

        :return: A machine description
        :rtype: :py:class:`spinn_machine.machine.Machine`
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

    def is_connected(self, connection=None):
        """ Determines if the board can be contacted

        :param connection: The connection which is to be tested.  If none,\
                    all connections will be tested, and the board will be\
                    considered to be connected if any one connection works.
        :type connection:\
                    :py:class:`spinnman.connections.abstract_connection.AbstractConnection`
        :return: True if the board can be contacted, False otherwise
        :rtype: bool
        :raise None: No known exceptions are raised
        """
        if connection is not None:
            if connection.is_connected():
                return True
            return False
        else:
            for connection in self._scamp_connections.values():
                if connection.is_connected():
                    return True
            return False

    def get_scamp_version(self, n_retries=3, timeout=1):
        """ Get the version of scamp which is running on the board

        :param n_retries: The number of times to retry getting the version
        :type n_retries: int
        :param timeout: The timeout for each retry in seconds
        :type timeout: int
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
        process = GetVersionProcess(self._get_random_connection(
            self._scamp_connections))
        return process.get_version()

    def boot_board(self, board_version):
        """ Attempt to boot the board.  No check is performed to see if the\
            board is already booted.

        :param board_version: The version of the board e.g. 3 for a SpiNN-3\
                    board or 5 for a SpiNN-5 board.
        :type board_version: int
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If the\
                    board version is not known
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    communicating with the board
        """
        logger.debug("Attempting to boot version {} board".format(
            board_version))
        boot_messages = SpinnakerBootMessages(board_version)
        for boot_message in boot_messages.messages:
            self._boot_send_connection.send_boot_message(boot_message)

    def ensure_board_is_ready(self, board_version, n_retries=3):
        """ Ensure that the board is ready to interact with this version\
            of the transceiver.  Boots the board if not already booted and\
            verifies that the version of SCAMP running is compatible with\
            this transceiver.

        :param board_version: The version of the board e.g. 3 for a SpiNN-3\
                    board or 5 for a SpiNN-5 board.
        :type board_version: int
        :param n_retries: The number of times to retry booting
        :type n_retries: int
        :return: The version identifier
        :rtype: :py:class:`spinnman.model.version_info.VersionInfo`
        :raise: spinnman.exceptions.SpinnmanIOException:
                    * If there is a problem booting the board
                    * If the version of software on the board is not\
                      compatible with this transceiver
        """
        version_info = None
        tries_to_go = n_retries + 1
        while version_info is None and tries_to_go > 0:
            try:
                version_info = self.get_scamp_version()
            except SpinnmanTimeoutException:
                self.boot_board(board_version)
                tries_to_go -= 1
            except SpinnmanIOException:
                raise SpinnmanUnexpectedResponseCodeException(
                    "We currently cannot communicate with your board, please "
                    "rectify this, and try again", "", "")

        if version_info is None:
            raise SpinnmanIOException("Could not boot the board")
        if (version_info.name != _SCAMP_NAME or
                version_info.version_number != _SCAMP_VERSION):
            raise SpinnmanIOException(
                "The board is currently booted with {}"
                " {} which is incompatible with this transceiver, "
                "required version is {} {}".format(
                    version_info.name, version_info.version_number,
                    _SCAMP_NAME, _SCAMP_VERSION))

        # Change the default SCP timeout on the machine, keeping the old one to
        # revert at close
        for scamp_connection in self._scamp_connections:
            process = SendSingleCommandProcess(
                self._machine, [scamp_connection])
            process.execute(SCPIPTagTTORequest(
                scamp_connection.chip_x, scamp_connection.chip_y, 2))

        return version_info

    def get_cpu_information(self, core_subsets=None):
        """ Get information about the processors on the board

        :param core_subsets: A set of chips and cores from which to get\
                    the information.  If not specified, the information from\
                    all of the cores on all of the chips on the board are\
                    obtained
        :type core_subsets: :py:class:`spinnman.model.core_subsets.CoreSubsets`
        :return: An iterable of the cpu information for the selected cores, or\
                    all cores if core_subsets is not specified
        :rtype: iterable of :py:class:`spinnman.model.cpu_info.CPUInfo`
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
        # Ensure that the information about each chip is present
        if self._machine is None:
            self._update_machine()

        # Get all the cores if the subsets are not given
        if core_subsets is None:
            core_subsets = CoreSubsets()
            for chip_info in self._chip_info.itervalues():
                x = chip_info.x
                y = chip_info.y
                for p in chip_info.virtual_core_ids:
                    core_subsets.add_processor(x, y, p)

        process = GetCPUInfoProcess(self._machine, self._scamp_connections)
        return process.get_cpu_info(self._chip_info, core_subsets)

    def get_user_0_register_address_from_core(self, x, y, p):
        """Get the address of user 0 for a given processor on the board

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
        # Ensure that the information about each chip is present
        if self._machine is None:
            self._update_machine()

        # check the chip exists in the infos
        if not (x, y) in self._chip_info:
            raise SpinnmanInvalidParameterException(
                "x, y", "{}, {}".format(x, y),
                "Not a valid chip on the current machine")

        # collect the chip info for the associated chip
        chip_info = self._chip_info[(x, y)]

        # check that p is a valid processor for this chip
        if p not in chip_info.virtual_core_ids:
            raise SpinnmanInvalidParameterException(
                "p", str(p), "Not a valid core on chip {}, {}".format(x, y))

        # locate the base address for this chip info
        base_address = (chip_info.cpu_information_base_address +
                        (constants.CPU_INFO_BYTES * p))
        base_address += constants.CPU_USER_0_START_ADDRESS
        return base_address

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
        :type core_subsets: :py:class:`spinnman.model.core_subsets.CoreSubsets`
        :return: An iterable of the buffers, which may not be in the order\
                    of core_subsets
        :rtype: iterable of :py:class:`spinnman.model.io_buffer.IOBuffer`
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
        # Ensure that the information about each chip is present
        if self._machine is None:
            self._update_machine()

        process = ReadIOBufProcess(self._machine, self._scamp_connections)
        return process.read_iobuf(self._chip_info, core_subsets)

    def get_iobuf_from_core(self, x, y, p):
        """ Get the contents of IOBUF for a given core

        :param x: The x-coordinate of the chip containing the processor
        :type x: int
        :param y: The y-coordinate of the chip containing the processor
        :type y: int
        :param p: The id of the processor to get the IOBUF for
        :type p: int
        :return: An IOBUF buffer
        :rtype: :py:class:`spinnman.model.io_buffer.IOBuffer`
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
        :type state: :py:class:`spinnman.model.cpu_state.CPUState`
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
        process = SendSingleCommandProcess(
            self._machine, self._scamp_connections)
        response = process.execute(SCPCountStateRequest(app_id, state))
        return response.count

    def execute(self, x, y, processors, executable, app_id, n_bytes=None):
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
        :type executable:\
                    :py:class:`spinnman.data.abstract_data_reader.AbstractDataReader`\
                    or bytearray
        :param app_id: The id of the application with which to associate the\
                    executable
        :type app_id: int
        :param n_bytes: The size of the executable data in bytes.  If not\
                    specified:
                        * If data is an AbstractDataReader, an error is raised
                        * If data is a bytearray, the length of the bytearray\
                          will be used
                        * If data is an int, 4 will be used
        :type n_bytes: int
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
        self.write_memory(x, y, 0x67800000, executable, n_bytes)

        # Request the start of the executable
        process = SendSingleCommandProcess(
            self._machine, self._scamp_connections)
        process.execute(
            SCPApplicationRunRequest(app_id, x, y, processors))

        # Release the lock
        self._release_chip_execute_lock(x, y)

    def _get_next_nearest_neighbour_id(self):
        self._next_nearest_neighbour_condition.acquire()
        next_nearest_neighbour_id = self._next_nearest_neighbour_id
        self._next_nearest_neighbour_id = \
            (self._next_nearest_neighbour_id + 1) % 127
        self._next_nearest_neighbour_condition.release()
        return next_nearest_neighbour_id

    def execute_flood(self, core_subsets, executable, app_id, n_bytes=None):
        """ Start an executable running on multiple places on the board.  This\
            will be optimized based on the selected cores, but it may still\
            require a number of communications with the board to execute.

        :param core_subsets: Which cores on which chips to start the executable
        :type core_subsets: :py:class:`spinnman.model.core_subsets.CoreSubsets`
        :param executable: The data that is to be executed.  Should be one of\
                    the following:
                    * An instance of AbstractDataReader
                    * A bytearray
        :type executable:\
                    :py:class:`spinnman.data.abstract_data_reader.AbstractDataReader`\
                    or bytearray
        :param app_id: The id of the application with which to associate the\
                    executable
        :type app_id: int
        :param n_bytes: The size of the executable data in bytes.  If not\
                    specified:
                        * If data is an AbstractDataReader, an error is raised
                        * If data is a bytearray, the length of the bytearray\
                          will be used
                        * If data is an int, 4 will be used
        :type n_bytes: int
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
        # Lock against other executables
        self._get_flood_execute_lock()

        # Flood fill the system with the binary
        self.write_memory_flood(0x67800000, executable, n_bytes)

        # Execute the binary on the cores on the chips where required
        process = ApplicationRunProcess(self._machine, self._scamp_connections)
        process.run(app_id, core_subsets)

        # Release the lock
        self._release_flood_execute_lock()

    def write_memory(self, x, y, base_address, data, n_bytes=None, offset=0,
                     cpu=0):
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
        :param offset: The offset from which the valid data begins
        :type offset: int
        :param cpu: The optional cpu to write to
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
        process = WriteMemoryProcess(self._scamp_connections)
        if isinstance(data, AbstractDataReader):
            process.write_memory_from_reader(x, y, cpu, base_address, data,
                                             n_bytes)
        elif isinstance(data, (int, long)):
            data_to_write = bytearray(4)
            for i in range(0, 4):
                data_to_write[i] = (data >> (8 * i)) & 0xFF
            process.write_memory_from_bytearray(x, y, cpu, base_address,
                                                data_to_write, 0, 4)
        else:
            if n_bytes is None:
                n_bytes = len(data)
            process.write_memory_from_bytearray(x, y, cpu, base_address, data,
                                                offset, n_bytes)

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
        :param offset: The offset where the valid data starts
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

        process = WriteMemoryProcess(self._scamp_connections)
        if isinstance(data, AbstractDataReader):
            process.write_link_memory_from_reader(x, y, cpu, base_address,
                                                  data, n_bytes)
        elif isinstance(data, (int, long)):
            data_to_write = bytearray(4)
            for i in range(0, 4):
                data_to_write[i] = (data >> (8 * i)) & 0xFF
            process.write_link_memory_from_bytearray(x, y, cpu, base_address,
                                                     data_to_write, 0, 4)
        else:
            if n_bytes is None:
                n_bytes = len(data)
            process.write_link_memory_from_bytearray(x, y, cpu, base_address,
                                                     data, offset, n_bytes)

    def write_memory_flood(self, base_address, data, n_bytes=None, offset=0):
        """ Write to the SDRAM of all chips.

        :param base_address: The address in SDRAM where the region of memory\
                    is to be written
        :type base_address: int
        :param data: The data that is to be written.  Should be one of\
                    the following:
                    * An instance of AbstractDataReader
                    * A bytearray
                    * A single integer
        :type data:\
                    :py:class:`spinnman.data.abstract_data_reader.AbstractDataReader`\
                    or bytearray or int
        :param n_bytes: The amount of data to be written in bytes.  If not\
                    specified:
                        * If data is an AbstractDataReader, an error is raised
                        * If data is a bytearray, the length of the bytearray\
                          will be used
                        * If data is an int, 4 will be used
                        * If n_bytes is less than 0
        :type n_bytes: int
        :param offset: The offset where the valid data starts
        :type offset: int
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
        process = WriteMemoryFloodProcess(self._scamp_connections)
        if isinstance(data, AbstractDataReader):
            process.write_memory_from_reader(
                nearest_neighbour_id, base_address, data, n_bytes)
        elif isinstance(data, (int, long)):
            data_to_write = bytearray(4)
            for i in range(0, 4):
                data_to_write[i] = (data >> (8 * i)) & 0xFF
            process.write_memory_from_bytearray(
                nearest_neighbour_id, base_address, data_to_write, 0, 4)
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

        process = ReadMemoryProcess(self._scamp_connections)
        return process.read_memory(x, y, cpu, base_address, length)

    def read_neighbour_memory(self, x, y, link, base_address, length, cpu=0):
        """ Read some areas of memory on a neighbouring chip using a LINK_READ
        SCP command. If sent to a BMP, this command can be used to communicate
        with the FPGAs' debug registers.

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

        process = ReadMemoryProcess(self._scamp_connections)
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
        process = SendSingleCommandProcess(self._machine,
                                           self._scamp_connections)
        process.execute(SCPAppStopRequest(app_id))

    def send_signal(self, app_id, signal):
        """ Send a signal to an application

        :param app_id: The id of the application to send to
        :type app_id: int
        :param signal: The signal to send
        :type signal: :py:class:`spinnman.messages.scp.scp_signal.SCPSignal`
         :py:class:`spinnman.messages.scp.scp_signal.SCPSignal'
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
        process = SendSingleCommandProcess(self._machine,
                                           self._scamp_connections)
        process.execute(SCPSendSignalRequest(app_id, signal))

    def set_leds(self, x, y, cpu, led_states):
        """ Set LED states.
        :param x: The x-coordinate of the chip on which to set the LEDs
        :type x: int
        :param y: The x-coordinate of the chip on which to set the LEDs
        :type y: int
        :param cpu: The CPU of the chip on which to set the LEDs
        :type cpu: int
        :param led_states: A dictionary mapping LED index to state with 0 being
                           off, 1 on and 2 inverted.
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
        process = SendSingleCommandProcess(self._machine,
                                           self._scamp_connections)
        process.execute(SCPLEDRequest(x, y, cpu, led_states))

    def locate_spinnaker_connection_for_board_address(self, board_address):
        """ Find a connection that matches the given board IP address

        :param board_address: The IP address of the ethernet connection on the\
                    baord
        :type board_address: str
        :return: A connection for the given IP address, or None if no such\
                    connection exists
        :rtype:\
                    :py:class:`spinnman.connections.udp_packet_connections.udp_spinnaker_connection.UDPSpinnakerConnection`
        """
        if board_address in self._udp_scamp_connections:
            return self._udp_scamp_connections[board_address]
        return None

    def set_ip_tag(self, ip_tag):
        """ Set up an ip tag

        :param ip_tag: The tag to set up; note board_address can be None, in\
                    which case, the tag will be assigned to all boards
        :type ip_tag: :py:class:`spinn_machine.tags.iptag.IPTag`
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

        # Get the connections - if the tag specifies a connection, use that,
        # otherwise apply the tag to all connections
        connections = list()
        if ip_tag.board_address is not None:
            connection = self.locate_spinnaker_connection_for_board_address(
                ip_tag.board_address)
            if connection is None:
                raise SpinnmanInvalidParameterException(
                    "ip_tag", str(ip_tag),
                    "The given board address is not recognized")
            connections.append(connection)
        else:
            connections = self._scamp_connections

        for connection in connections:

            # Convert the host string
            host_string = ip_tag.ip_address
            if host_string == "localhost" or host_string == ".":
                host_string = connection.local_ip_address
            ip_string = gethostbyname(host_string)
            ip_address = bytearray(inet_aton(ip_string))

            process = SendSingleCommandProcess(self._machine, [connection])
            process.execute(SCPIPTagSetRequest(
                connection.chip_x, connection.chip_y, ip_address, ip_tag.port,
                ip_tag.tag, strip=ip_tag.strip_sdp))

    def set_reverse_ip_tag(self, reverse_ip_tag):
        """ Set up a reverse ip tag

        :param reverse_ip_tag: The reverse tag to set up; note board_address\
                    can be None, in which case, the tag will be assigned to\
                    all boards
        :type reverse_ip_tag:\
                    :py:class:`spinn_machine.tags.reverse_ip_tag.ReverseIPTag`
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

        if (reverse_ip_tag.port == constants.SCP_SCAMP_PORT or
                reverse_ip_tag.port ==
                constants.UDP_BOOT_CONNECTION_DEFAULT_PORT):
            raise SpinnmanInvalidParameterException(
                "reverse_ip_tag.port", reverse_ip_tag.port,
                "The port number for the reverese ip tag conflicts with"
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
                    "The given board address is not recognized")
            connections.append(connection)
        else:
            connections = self._scamp_connections

        for connection in connections:
            process = SendSingleCommandProcess(self._machine, [connection])
            process.execute(SCPReverseIPTagSetRequest(
                connection.chip_x, connection.chip_y,
                reverse_ip_tag.destination_x, reverse_ip_tag.destination_y,
                reverse_ip_tag.destination_p,
                reverse_ip_tag.port, reverse_ip_tag.tag,
                reverse_ip_tag.sdp_port))

    def clear_ip_tag(self, tag, connection=None, board_address=None):
        """ Clear the setting of an ip tag

        :param tag: The tag id
        :type tag: int
        :param connection: Connection where the tag should be cleard.  If not\
                    specified, all SCPSender connections will send the message\
                    to clear the tag
        :type connection:\
                    :py:class:`spinnman.connections.abstract_scp_sender.AbstractSCPSender`
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
            process = SendSingleCommandProcess(self._machine, [connection])
            process.execute(SCPIPTagClearRequest(
                connection.chip_x, connection.chip_y, tag))

    def get_tags(self, connection=None):
        """ Get the current set of tags that have been set on the board

        :param connection: Connection from which the tags should be received.\
                    If not specified, all SCPSender connections will be\
                    queried and the response will be combined.
        :type connection:\
                    :py:class:`spinnman.connections.abstract_scp_sender.AbstractSCPSender`
        :return: An iterable of tags
        :rtype: iterable of\
                    :py:class:`spinn_machine.tags.abstract_tag.AbstractTag`
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
            process = GetTagsProcess(self._machine, connections)
            all_tags.extend(process.get_tags(connection))
        return all_tags

    def load_multicast_routes(self, x, y, routes, app_id):
        """ Load a set of multicast routes on to a chip

        :param x: The x-coordinate of the chip onto which to load the routes
        :type x: int
        :param y: The y-coordinate of the chip onto which to load the routes
        :type y: int
        :param routes: An iterable of multicast routes to load
        :type routes: iterable of\
                    :py:class:`spinnmachine.multicast_routing_entry.MulticastRoutingEntry`
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

        process = LoadRoutesProcess(self._machine, self._scamp_connections)
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
        if self._machine is None:
            self._update_machine()
        chip_info = self._chip_info[(x, y)]
        base_address = chip_info.router_table_copy_address()
        process = GetRoutesProcess(self._scamp_connections, app_id)
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
        process = SendSingleCommandProcess(
            self._machine, self._scamp_connections)
        process.execute(SCPRouterClearRequest(x, y))

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
        process = ReadRouterDiagnosticsProcess(
            self._machine, self._scamp_connections)
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
        :return: None
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
                " By doing this, other runs occuring on this machine will be "
                "forced to use this new configuration untill the machine is "
                "reset. Please also note that these changes will make the"
                " the reports from ybug not correct."
                "This has been executed and is trusted that the end user knows"
                " what they are doing")
        memory_position = (constants.ROUTER_REGISTER_BASE_ADDRESS +
                           constants.ROUTER_FILTER_CONTROLS_OFFSET +
                           (position *
                            constants.ROUTER_DIAGNOSTIC_FILTER_SIZE))

        process = SendSingleCommandProcess(
            self._machine, self._scamp_connections)
        process.execute(SCPWriteMemoryRequest(
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
        process = SendSingleCommandProcess(
            self._machine, self._scamp_connections)
        response = process.execute(
            SCPReadMemoryRequest(x, y, memory_position, 4))
        return DiagnosticFilter.read_from_int(struct.unpack_from(
            "<I", response.data, response.offset)[0])

    def clear_router_diagnostic_counters(self, x, y, enable=True,
                                         counter_ids=range(0, 16)):
        """ Clear router diagnostic information om a chip

        :param x: The x-coordinate of the chip
        :type x: int
        :param y: The y-coordinate of the chip
        :type y: int
        :param enable: True (default) if the counters should be enabled
        :type enable: bool
        :param counter_ids: The ids of the counters to reset (all by default)\
                    and enable if enable is True; each must be between 0 and 15
        :type counter_ids: array-like of int
        :return: None
        :rtype: Nothing is returned
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
                    "counter_id", counter_id, "Diagnostic counter ids must be"
                                              " between 0 and 15")
            clear_data |= 1 << counter_id
        if enable:
            for counter_id in counter_ids:
                clear_data |= 1 << counter_id + 16
        process = SendSingleCommandProcess(
            self._machine, self._scamp_connections)
        process.execute(SCPWriteMemoryRequest(
            x, y, 0xf100002c, struct.pack("<I", clear_data)))

    def close(self, close_original_connections=True):
        """ Close the transceiver and any threads that are running

        :param close_original_connections: If True, the original connections\
                    passed to the transceiver in the constructor are also\
                    closed.  If False, only newly discovered connections are\
                    closed.
        :return: Nothing is returned
        :rtype: None
        :raise None: No known exceptions are raised
        """

        for connection in self._all_connections:
            if (close_original_connections or
                    connection not in self._original_connections):
                connection.close()

    def register_listener(self, callback, recieve_port_no,
                          connection_type, traffic_type, hostname=None):
        """ Register a callback for a certain type of traffic

        :param callback: Function to be called when a packet is received
        :type callback: function(packet)
        :param recieve_port_no: The port number to listen on
        :type recieve_port_no: int
        :param connection_type: The type of the connection
        :param traffic_type: The type of traffic expected on the connection
        :param hostname: The optional hostname to listen on
        :type hostname: str
        """
        if recieve_port_no in self._receiving_connections:
            connection = self._receiving_connections[recieve_port_no]
            if connection_type == connection.connection_type():
                connection.register_callback(callback)
            else:
                raise SpinnmanInvalidParameterException(
                    "There is already a connection on this port number which "
                    "does not support reception of this message type. Please "
                    "try again with antoher port number", "", "")
        else:
            if connection_type == constants.CONNECTION_TYPE.SDP_IPTAG:
                connection = IPTagConnection(hostname, recieve_port_no)
                connection.register_callback(callback, traffic_type)
                self._receiving_connections[recieve_port_no] = connection
            elif connection_type == constants.CONNECTION_TYPE.UDP_IPTAG:
                connection = StrippedIPTagConnection(hostname, recieve_port_no)
                connection.register_callback(callback, traffic_type)
                self._receiving_connections[recieve_port_no] = connection
            else:
                raise SpinnmanInvalidParameterException(
                    "Currently spinnman does not know how to register a "
                    "callback to a connection of type {}."
                    .format(connection_type), "", "")

    def __str__(self):
        return "transciever object connected to {} with {} connections"\
            .format(self._sending_connections[0].remote_ip_address,
                    len(self._sending_connections.keys()))

    def __repr__(self):
        return self.__str__()
