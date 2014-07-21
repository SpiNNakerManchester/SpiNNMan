from spinnman.connections.udp_connection import UDPConnection
from spinnman.connections.udp_boot_connection import UDPBootConnection
from spinnman.connections.udp_connection import UDP_CONNECTION_DEFAULT_PORT
from spinnman.connections._connection_queue import _ConnectionQueue

from spinnman.exceptions import SpinnmanUnsupportedOperationException
from spinnman.exceptions import SpinnmanTimeoutException
from spinnman.exceptions import SpinnmanInvalidParameterException
from spinnman.exceptions import SpinnmanIOException
from spinnman.exceptions import SpinnmanUnexpectedResponseCodeException

from spinnman.model.chip_info import ChipInfo
from spinnman.model.chip_info import _SYSTEM_VARIABLE_BASE_ADDRESS
from spinnman.model.chip_info import _SYSTEM_VARIABLE_BYTES
from spinnman.model.cpu_info import CPU_INFO_BYTES
from spinnman.model.cpu_info import CPUInfo
from spinnman.model.machine_dimensions import MachineDimensions
from spinnman.model.core_subsets import CoreSubsets


from spinnman.messages.spinnaker_boot.spinnaker_boot_messages import SpinnakerBootMessages
from spinnman.messages.scp.impl.scp_read_link_request import SCPReadLinkRequest
from spinnman.messages.scp.impl.scp_read_memory_request import SCPReadMemoryRequest
from spinnman.messages.scp.impl.scp_version_request import SCPVersionRequest
from spinnman.messages.scp.impl.scp_count_state_request import SCPCountStateRequest
from spinnman.messages.scp.scp_result import SCPResult

from spinnman._threads._scp_message_thread import _SCPMessageThread
from spinnman._threads._iobuf_thread import _IOBufThread

from spinn_machine.machine import Machine
from spinn_machine.chip import Chip
from spinn_machine.chip import CHIP_DEFAULT_SDRAM_AVAIABLE
from spinn_machine.sdram import SDRAM
from spinn_machine.processor import Processor
from spinn_machine.router import Router
from spinn_machine.router import ROUTER_DEFAULT_AVAILABLE_ENTRIES
from spinn_machine.router import ROUTER_DEFAULT_CLOCK_SPEED
from spinn_machine.link import Link

from collections import deque

import logging
from spinnman.messages.scp.impl.scp_write_memory_request import SCPWriteMemoryRequest

logger = logging.getLogger(__name__)

_SCAMP_NAME = "SC&MP"
_SCAMP_VERSION = 1.31


def create_transceiver_from_hostname(hostname, discover=True):
    """ Create a Transceiver by creating a UDPConnection to the given\
        hostname on port 17893 (the default SCAMP port), and a\
        UDPBootConnection on port 54321 (the default boot port),
        optionally discovering any additional links using the UDPConnection,\
        and then returning the transceiver created with the conjunction of the\
        created UDPConnection and the discovered connections

    :param hostname: The hostname or IP address of the board
    :type hostname: str
    :param discover: True if further connections should be discovered, False\
                otherwise
    :type discover: bool
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
    connection = UDPConnection(remote_host=hostname)
    boot_connection = UDPBootConnection(remote_host=hostname)
    return Transceiver(connections=[connection, boot_connection],
            discover=discover)


class Transceiver(object):
    """ An encapsulation of various communications with the spinnaker board.\
        Note that the methods of this class are designed to be thread-safe;\
        thus you can make multiple calls to the same (or different) methods\
        from multiple threads and expect each call to work as if it had been\
        called sequentially, although the order of returns is not guaranteed.\
        Note also that with multiple connections to the board, using multiple\
        threads in this way may result in an increase in the overall speed of\
        operation, since the multiple calls may be made separately over the\
        set of given connections.
    """

    def __init__(self, connections=None, discover=True):
        """

        :param connections: An iterable of connections to the board.  If not\
                    specified, no communication will be possible until\
                    connections are specified.
        :type connections: iterable of\
                    :py:class:`spinnman.connections.abstract_connection.AbstractConnection`
        :param discover: Determines if discovery should take place.  If not\
                    specified, an attempt will be made to discover connections\
                    to the board.
        :type discover: bool
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    communicating with the board
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If a packet\
                    is received that is not in the valid format
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If a\
                    packet is received that has invalid parameters
        :raise spinnman.exceptions.SpinnmanUnexpectedResponseCodeException: If\
                    a response indicates an error during the exchange
        """

        # Place to keep the current machine
        self._machine = None

        # Place to keep the known chip information
        self._chip_info = dict()

        # Create a connection list
        self._connections = None
        if connections is not None:
            self._connections = list(connections)
        else:
            self._connections = list()
        self._original_connections = set(self._connections)

        # Update the list of UDP connections
        self._udp_connections = dict()
        for connection in self._connections:
            if isinstance(connection, UDPConnection):
                self._udp_connections[(connection._remote_ip_address,
                        connection._remote_port)] = connection

        # Update the queues for the given connections
        self._connection_queues = dict()
        self._update_connection_queues()

        # Discover any new connections, and update the queues if requested
        if discover:
            self.discover_connections()

    def _update_connection_queues(self):
        """ Creates and deletes queues of connections depending upon what\
            connections are now available

        :return: Nothing is returned
        :rtype: None
        :raise None: No known exceptions are raised
        """
        for connection in self._connections:

            # Only add a new queue if there isn't one currently
            if connection not in self._connection_queues:
                self._connection_queues[connection] =\
                        _ConnectionQueue(connection)
                self._connection_queues[connection].start()

    def _find_best_connection_queue(self, message, response_required,
            connection=None):
        """ Finds the best connection queue to use to send a message

        :param message: The message to send
        :type message: One of:
                    * :py:class:`spinnman.messages.sdp.sdp_message.SDPMessage`
                    * :py:class:`spinnman.messages.scp.abstract_scp_request.AbstractSCPRequest`
                    * :py:class:`spinnman.messages.multicast_message.MulticastMessage`
                    * :py:class:`spinnman.messages.spinnaker_boot.spinnaker_boot_message.SpinnakerBootMessage`
        :param response_required: True if a response is required, False\
                    otherwise
        :type response_required: bool
        :param connection: An optional connection to use
        :type connection:\
                    :py:class:`spinnman.connections.abstract_connection.AbstractConnection`
        :return: The best connection queue
        :rtype: :py:class:`spinnman.connections._connection_queue.ConnectionQueue`
        :raise spinnman.exceptions.SpinnmanUnsupportedOperationException: If\
                    no connection can send the type of message given
        """
        best_connection_queue = None

        # If a connection is given, use it
        if connection != None:
            best_connection_queue = self._connection_queues[connection]

            # If the connection doesn't support the message,
            # reject the connection, and allow the error to be raised later
            if not best_connection_queue.message_type_supported(message):
                best_connection_queue = None
        else:

            # Find the least congested way that supports the message type
            best_connection_queue_size = None
            for connection_queue in self._connection_queues.values():
                if connection_queue.message_type_supported(
                        message, response_required):
                    connection_queue_size = connection_queue.queue_length
                    if (best_connection_queue is None
                            or connection_queue_size
                                    < best_connection_queue_size):
                        best_connection_queue = connection_queue
                        best_connection_queue_size = connection_queue_size

        # If no supported queue was found, raise an exception
        if best_connection_queue is None:
            raise SpinnmanUnsupportedOperationException(
                    "Sending and receiving {}".format(message.__class__))

        return best_connection_queue

    def send_message(self, message, response_required, connection=None,
            timeout=1, get_callback=False):
        """ Sends a message using one of the connections, and gets a response\
            if requested

        :param message: The message to send
        :type message: One of:
                    * :py:class:`spinnman.messages.sdp.sdp_message.SDPMessage`
                    * :py:class:`spinnman.messages.scp.abstract_scp_request.AbstractSCPRequest`
                    * :py:class:`spinnman.messages.multicast_message.MulticastMessage`
                    * :py:class:`spinnman.messages.spinnaker_boot.spinnaker_boot_message.SpinnakerBootMessage`
        :param response_required: True if a response is required, False\
                    otherwise
        :type response_required: bool
        :param connection: An optional connection to use
        :type connection:\
                    :py:class:`spinnman.connections.abstract_connection.AbstractConnection`
        :param timeout: Timeout to use when waiting for a response
        :type timeout: int
        :param get_callback: Determines if the function should return the\
                    callback which can be used to send messages asynchronously
        :type get_callback: bool
        :return:
                    * If get_callback is False, and response_required is True,\
                      the response
                    * If get_callback is False, and response_required is\
                      False, None
                    * If get_callback is True, the callback
        :rtype:
                    * If get_callback is False, and response_required is True,
                      and the message type is AbstractSCPRequest then\
                      :py:class:`spinnman.messages.scp.abstract_scp_response.AbstractSCPResponse`
                    * If get_callback is False, and response_required is True,
                      then the same type as the message
                    * If get_callback is False, and response_required is False,
                      then None
                    * If get_callback is True, then\
                      :py:class:`spinnman.connections._message_callback._MessageCallback`
        :raise spinnman.exceptions.SpinnmanTimeoutException: If there is a\
                    timeout before a message is received
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If one\
                    of the fields of the received message is invalid
        :raise spinnman.exceptions.SpinnmanInvalidPacketException:
                    * If the message is not one of the indicated types
                    * If a packet is received is not a valid response
        :raise spinnman.exceptions.SpinnmanUnsupportedOperationException: If\
                    no connection can send the type of message given
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    sending the message or receiving the response
        """
        best_connection_queue = self._find_best_connection_queue(message,
                response_required, connection)
        logger.debug("Sending message with {}".format(best_connection_queue))

        # Send the message with the best queue
        if get_callback:
            return best_connection_queue.send_message_non_blocking(
                    message, response_required, timeout)
        return best_connection_queue.send_message(
                message, response_required, timeout)

    def _send_scp_message(
            self, message, retry_codes=(
                SCPResult.RC_P2P_TIMEOUT, SCPResult.RC_TIMEOUT,
                SCPResult.RC_LEN),
            n_retries=10, timeout=1, connection=None):
        """ Sends an SCP message, and gets a response

        :param message: The message to send
        :type message:\
                    :py:class:`spinnman.messages.scp.abstract_scp_request.AbstractSCPRequest`
        :param retry_codes: The response codes which will result in a\
                    retry if received as a response
        :type retry_codes: iterable of\
                    :py:class:`spinnman.messages.scp.scp_result.SCPResult`
        :param n_retries: The number of times to retry when a retry code is\
                received
        :type n_retries: int
        :param timeout: The timeout to use when receiving a response
        :type timeout: int
        :param connection: The connection to use
        :type connection:\
                    :py:class:`spinnman.connections.abstract_connection.AbstractConnection`
        :return: The received response, or the callback if get_callback is True
        :rtype: :py:class:`spinnman.messages.scp.abstract_scp_response.AbstractSCPResponse`
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
        thread = _SCPMessageThread(
                transceiver=self, message=message, retry_codes=retry_codes,
                n_retries=n_retries, timeout=timeout, connection=connection)
        thread.start()
        return thread.get_response()

    def _make_chip(self, chip_details):
        """ Creates a chip from a ChipInfo structure

        :param chip_details: The ChipInfo structure to create the chip\
                    from
        :type chip_details: \
                    :py:class:`spinnman.model.chip_info.ChipInfo`
        :return: The created chip
        :rtype: :py:class:`spinn_machine.chip.Chip`
        """

        # Create the processor list
        processors = list()
        for virtual_core_id in chip_details.virtual_core_ids:
            processors.append(Processor(
                    virtual_core_id, chip_details.cpu_clock_mhz * 1000000,
                    virtual_core_id == 0))

        # Create the router - add the links later during search
        router = Router(
                links=list(), emergency_routing_enabled=False,
                clock_speed=ROUTER_DEFAULT_CLOCK_SPEED,
                n_available_multicast_entries=ROUTER_DEFAULT_AVAILABLE_ENTRIES
                    - chip_details.first_free_router_entry)

        # Create the chip
        chip = Chip(
                x=chip_details.x, y=chip_details.y, processors=processors,
                router=router, sdram=SDRAM(CHIP_DEFAULT_SDRAM_AVAIABLE),
                ip_address=chip_details.ip_address)
        return chip

    def _update_machine(self):
        """ Get the current machine status and store it
        """

        # Ask the chip at 0, 0 for details
        logger.debug("Getting details of chip 0, 0")
        response = self._send_scp_message(SCPReadMemoryRequest(
                x=0, y=0, base_address=_SYSTEM_VARIABLE_BASE_ADDRESS,
                size=_SYSTEM_VARIABLE_BYTES))
        chip_0_0_details = ChipInfo(response.data)
        self._chip_info[(0, 0)] = chip_0_0_details
        chip_0_0 = self._make_chip(chip_0_0_details)

        # Create a machine with chip 0, 0
        self._machine = Machine([chip_0_0])

        # Perform a search of the chips via the links
        search = deque([(chip_0_0, chip_0_0_details.links_available)])
        while len(search) > 0:
            (chip, links) = search.pop()

            # Examine the links of the chip to find the next chips
            for link in links:
                try:
                    logger.debug(
                            "Searching down link {} from chip {}, {}".format(
                                    link, chip.x, chip.y))
                    response = self._send_scp_message(SCPReadLinkRequest(
                        x=chip.x, y=chip.y, link=link,
                        base_address=_SYSTEM_VARIABLE_BASE_ADDRESS,
                        size=_SYSTEM_VARIABLE_BYTES))
                    new_chip_details = ChipInfo(response.data)

                    # Standard links use the opposite link id (with ids between
                    # 0 and 5) as default
                    opposite_link_id = (link + 3) % 6

                    # Update the defaults of any existing link
                    if chip.router.is_link(opposite_link_id):
                        opposite_link = chip.router.get_link(opposite_link_id)
                        opposite_link.multicast_default_to = link
                        opposite_link.multicast_default_from = link
                    else:

                        # If the link doesn't exist, don't set a default for
                        # this link yet
                        opposite_link_id = None

                    # Add the link to the current chip
                    new_link = Link(
                            source_x=chip.x, source_y=chip.y,
                            source_link_id=link,
                            destination_x=new_chip_details.x,
                            destination_y=new_chip_details.y,
                            multicast_default_from=opposite_link_id,
                            multicast_default_to=opposite_link_id)
                    chip.router.add_link(new_link)

                    # Add the new chip if it doesn't exist
                    if not self._machine.is_chip_at(
                            new_chip_details.x, new_chip_details.y):
                        logger.debug("Found new chip {}, {}".format(
                                new_chip_details.x, new_chip_details.y))
                        new_chip = self._make_chip(new_chip_details)
                        self._machine.add_chip(new_chip)
                        self._chip_info[(new_chip.x,
                                new_chip.y)] = new_chip_details
                        search.append(
                                (new_chip, new_chip_details.links_available))

                except SpinnmanUnexpectedResponseCodeException:

                    # If there is an error, assume the link is down
                    pass

    def discover_connections(self):
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
        self._update_machine()

        # Find all the new connections via the machine ethernet-connected chips
        new_connections = list()
        for ethernet_connected_chip in self._machine.ethernet_connected_chips:
            if (ethernet_connected_chip.ip_address,
                    UDP_CONNECTION_DEFAULT_PORT) not in self._udp_connections:
                new_connection = UDPConnection(
                        remote_host=ethernet_connected_chip.ip_address)
                new_connections.append(new_connection)
                self._connections.append(new_connection)
                self._udp_connections[(ethernet_connected_chip.ip_address,
                    UDP_CONNECTION_DEFAULT_PORT)] = new_connection

        # Update the connection queues after finding new connections
        self._update_connection_queues()

        return new_connections

    def get_connections(self):
        """ Get the currently known connections to the board, made up of those\
            passed in to the transceiver and those that are discovered during\
            calls to discover_connections.  No further discovery is done here.

        :return: An iterable of connections known to the transciever
        :rtype: iterable of\
                    :py:class:`spinnman.connections.abstract_connection.AbstractConnection`
        :raise None: No known exceptions are raised
        """
        return self._connections

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
        for connection in self._connections:
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
        response = self._send_scp_message(
                message=SCPVersionRequest(x=0, y=0, p=0),
                n_retries=n_retries, timeout=timeout)
        return response.version_info

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
            self.send_message(boot_message, response_required=False)

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

        if version_info is None:
            raise SpinnmanIOException("Could not boot the board")
        if (version_info.name != _SCAMP_NAME
                or version_info.version_number != _SCAMP_VERSION):
            raise SpinnmanIOException("The board is currently booted with {}"
                    " {} which is incompatible with this transceiver".format(
                            version_info.name,
                            version_info.version_number))
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

        # Go through the requested chips
        callbacks = list()
        callback_coordinates = list()
        for core_subset in core_subsets:
            x = core_subset.x
            y = core_subset.y

            if not (x, y) in self._chip_info:
                raise SpinnmanInvalidParameterException(
                        "x, y", "{}, {}".format(x, y),
                        "Not a valid chip on the current machine")
            chip_info = self._chip_info[(x, y)]

            for p in core_subset.processor_ids:
                if p not in chip_info.virtual_core_ids:
                    raise SpinnmanInvalidParameterException(
                            "p", p, "Not a valid core on chip {}, {}".format(
                                    x, y))
                base_address = (chip_info.cpu_information_base_address
                        + (CPU_INFO_BYTES * p))
                callbacks.append(_SCPMessageThread(self, SCPReadMemoryRequest(
                                x, y, base_address, CPU_INFO_BYTES)))
                callback_coordinates.append((x, y, p))

        # Start all the callbacks (not done before to ensure that no errors
        # occur first
        for callback in callbacks:
            callback.start()

        # Gather the results
        for callback, (x, y, p) in zip(callbacks, callback_coordinates):
            yield CPUInfo(x, y, p, callback.get_response().data)

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
        return self.get_cpu_information(core_subsets)[0]

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

        # Get CPU Information for the requested chips
        cpu_information = self.get_cpu_information(core_subsets)

        # Go through the requested chips
        callbacks = list()
        for cpu_info in cpu_information:
            chip_info = self._chip_info[(cpu_info.x, cpu_info.y)]
            iobuf_bytes = chip_info.iobuf_size

            thread = _IOBufThread(
                    self, cpu_info.x, cpu_info.y, cpu_info.p,
                    cpu_info.iobuf_address, iobuf_bytes)
            thread.start()
            callbacks.append(thread)

        # Gather the results
        for callback in callbacks:
            yield callback.get_iobuf()

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
        response = self._send_scp_message(SCPCountStateRequest(app_id, state))
        return response.count

    def execute(self, x, y, p, executable, app_id):
        """ Start an executable running on a single core

        :param x: The x-coordinate of the chip on which to run the executable
        :type x: int
        :param y: The y-coordinate of the chip on which to run the executable
        :type y: int
        :param p: The core on the chip on which to run the application
        :type p: int
        :param executable: The data that is to be executed.  Should be one of\
                    the following:
                    * An instance of AbstractDataReader
                    * A bytearray
        :type executable: :py:class:`spinnman.data.abstract_data_reader.AbstractDataReader`\
                    or bytearray
        :param app_id: The id of the application with which to associate the\
                    executable
        :type app_id: int
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
        pass

    def execute_flood(self, core_subsets, executable, app_id):
        """ Start an executable running on multiple places on the board.  This\
            will be optimized based on the selected cores, but it may still\
            require a number of communications with the board to execute.

        :param core_subsets: Which cores on which chips to start the executable
        :type core_subsets: :py:class:`spinnman.model.core_subsets.CoreSubsets`
        :param executable: The data that is to be executed.  Should be one of\
                    the following:
                    * An instance of AbstractDataReader
                    * A bytearray
        :type executable: :py:class:`spinnman.data.abstract_data_reader.AbstractDataReader`\
                    or bytearray
        :param app_id: The id of the application with which to associate the\
                    executable
        :type app_id: int
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
        :raise spinnman.exceptions.SpinnmanUnexpectedResponseCodeException: If\
                    a response indicates an error during the exchange
        """
        pass

    def write_memory(self, x, y, base_address, data):
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
                    * A single integer
        :type data: :py:class:`spinnman.data.abstract_data_reader.AbstractDataReader`\
                    or bytearray or int
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
        :raise spinnman.exceptions.SpinnmanUnexpectedResponseCodeException: If\
                    a response indicates an error during the exchange
        """
        # Set up all the requests and get the callbacks
        logger.debug("Writing {} bytes of memory".format(len(data)))
        bytes_to_write = len(data)
        offset = 0
        address_to_write = base_address
        callbacks = list()
        while bytes_to_write > 0:
            data_size = bytes_to_write
            if data_size > 256:
                data_size = 256
            thread = _SCPMessageThread(self, SCPWriteMemoryRequest(
                    x, y, address_to_write, data[offset:(offset + data_size)]))
            thread.start()
            callbacks.append(thread)
            bytes_to_write -= data_size
            address_to_write += data_size
            offset += data_size

        # Go through the callbacks and check that the responses are OK
        for callback in callbacks:
            callback.get_response()

    def write_memory_flood(self, core_subsets, base_address, data):
        """ Write to the SDRAM of a number of chips.  This will be optimized\
            based on the selected cores, but it may still require a number\
            of communications with the board.

        :param core_subsets: Which chips to write the data to (the cores are\
                    ignored)
        :type core_subsets: :py:class:`spinnman.model.core_subsets.CoreSubsets`
        :param base_address: The address in SDRAM where the region of memory\
                    is to be written
        :type base_address: int
        :param data: The data that is to be written.  Should be one of\
                    the following:
                    * An instance of AbstractDataReader
                    * A bytearray
                    * A single integer
        :type data: :py:class:`spinnman.data.abstract_data_reader.AbstractDataReader`\
                    or bytearray or int
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
        pass

    def read_memory(self, x, y, base_address, length):
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

        # Set up all the requests and get the callbacks
        logger.debug("Reading {} bytes of memory".format(length))
        bytes_to_get = length
        address_to_read = base_address
        callbacks = list()
        while bytes_to_get > 0:
            data_size = bytes_to_get
            if data_size > 256:
                data_size = 256
            thread = _SCPMessageThread(self, SCPReadMemoryRequest(
                    x, y, address_to_read, data_size))
            thread.start()
            callbacks.append(thread)
            bytes_to_get -= data_size
            address_to_read += data_size

        # Go through the callbacks and return the responses in order
        for callback in callbacks:
            yield callback.get_response().data

    def send_signal(self, signal, app_id=None):
        """ Send a signal to an application

        :param signal: The signal to send
        :type signal: :py:class:`spinnman.messages.scp.scp_signal.SCPSignal`
        :param app_id: The id of the application to send to.  If not\
                    specified, the signal is sent to all applications
        :type app_id: int
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
        pass

    def set_ip_tag(self, ip_tag, connection=None):
        """ Set up an ip tag

        :param iptag: The iptag to set up
        :type iptag: :py:class:`spinnman.model.iptag.IPTag`
        :param connection: Connection where the tag should be set up.  If not\
                    specified, all SCPSender connections will send the message\
                    to set up the tag
        :type connection:\
                    :py:class:`spinnman.connections.abstract_scp_sender.AbstractSCPSender`
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    communicating with the board
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If a packet\
                    is received that is not in the valid format
        :raise spinnman.exceptions.SpinnmanInvalidParameterException:
                    * If the ip tag fields are incorrect
                    * If the connection cannot send SDP messages
                    * If a packet is received that has invalid parameters
        :raise spinnman.exceptions.SpinnmanUnexpectedResponseCodeException: If\
                    a response indicates an error during the exchange
        """
        pass

    def clear_ip_tag(self, tag, connection=None):
        """ Clear the setting of an ip tag

        :param tag: The tag id
        :type tag: int
        :param connection: Connection where the tag should be cleard.  If not\
                    specified, all SCPSender connections will send the message\
                    to clear the tag
        :type connection:\
                    :py:class:`spinnman.connections.abstract_scp_sender.AbstractSCPSender`
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
        pass

    def get_ip_tags(self, connection=None):
        """ Get the current set of ip tags that have been set on the board

        :param connection: Connection from which the tags should be received.\
                    If not specified, all SCPSender connections will be queried\
                    and the response will be combined.
        :type connection:\
                    :py:class:`spinnman.connections.abstract_scp_sender.AbstractSCPSender`
        :return: An iterable of ip tags
        :rtype: iterable of :py:class:`spinnman.model.iptag.IPTag`
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
        pass

    def load_multicast_routes(self, app_id, x, y, routes):
        """ Load a set of multicast routes on to a chip

        :param app_id: The id of the application to associate routes with
        :type app_id: int
        :param x: The x-coordinate of the chip onto which to load the routes
        :type x: int
        :param y: The y-coordinate of the chip onto which to load the routes
        :type y: int
        :param route_data_item: An iterable of multicast routes to load
        :type route_data_item: iterable of\
                    :py:class:`spinnman.model.multicast_routing_entry.MulticastRoute`
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
        pass

    def get_multicast_routes(self, x, y, app_id=None):
        """ Get the current multicast routes set up on a chip

        :param x: The x-coordinate of the chip from which to get the routes
        :type x: int
        :param y: The y-coordinate of the chip from which to get the routes
        :type y: int
        :param app_id: Optional application id of the routes.  If not\
                    specified all the routes will be returned.  If specified,\
                    the routes will be filtered so that only those for the\
                    given application are returned.
        :type app_id: int
        :return: An iterable of multicast routes
        :rtype: iterable of :py:class:`spinnman.model.multicast_routing_entry.MulticastRoute`
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    communicating with the board
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If a packet\
                    is received that is not in the valid format
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If a\
                    packet is received that has invalid parameters
        :raise spinnman.exceptions.SpinnmanUnexpectedResponseCodeException: If\
                    a response indicates an error during the exchange
        """
        pass

    def clear_multicast_routes(self, x, y, app_id=None):
        """ Remove all the multicast routes on a chip
        :param x: The x-coordinate of the chip on which to clear the routes
        :type x: int
        :param y: The y-coordinate of the chip on which to clear the routes
        :type y: int
        :param app_id: Optional application id of the routes.  If not\
                    specified all the routes will be cleared.  If specified,\
                    only the routes with the given application id will be\
                    removed.
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
        pass

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
        pass

    def send_multicast(self, x, y, multicast_message, connection=None):
        """ Sends a multicast message to the board

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
        pass

    def receive_multicast(self, x, y, timeout=None, connection=None):
        """ Receives a multicast message from the board

        :param x: The x-coordinate of the chip where the message should come\
                    from on the board
        :type x: int
        :param y: The y-coordinate of the chip where the message should come\
                    from on the board
        :type y: int
        :param timeout: Amount of time to wait for the message to arrive in\
                    seconds before a timeout.  If not specified, will wait\
                    indefinitely, or until the selected connection is closed
        :type timeout: int
        :param connection: A specific connection from which to receive the\
                    message.  If not specified, an appropriate connection is\
                    chosen automatically
        :type connection:\
                    :py:class:`spinnman.connections.abstract_multicast_receiver.AbstractMulticastReceiver`
        :return: The received message
        :rtype: :py:class:`spinnman.messages.multicast_message.MulticastMessage`
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    communicating with the board
        :raise spinnman.exceptions.SpinnmanUnsupportedOperationException:
                    * If there is no connection that supports reception over\
                      multicast (or the given connection does not)
                    * If there is no connection that can receive a packet\
                      from the selected chip (ignoring routing tables)
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If the\
                    message received is not a valid multicast message
        :raise spinnman.exceptions.SpinnmanInvalidParameterException:
                    * If the timeout value is not valid
                    * If the received packet has an invalid parameter
        """
        pass

    def send_sdp_message(self, sdp_message, connection=None):
        """ Sends an SDP message to the board

        :param sdp_message: The SDP message to send
        :type sdp_message: :py:class:`spinnman.messages.sdp.sdp_message.SDPMessage`
        :param connection: A specific connection over which to send the\
                    message.  If not specified, an appropriate connection is\
                    chosen automatically
        :type connection:\
                    :py:class:`spinnman.connections.abstract_sdp_sender.AbstractSDPSender`
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    communicating with the board
        :raise spinnman.exceptions.SpinnmanUnsupportedOperationException: If\
                    there is no connection that supports sending SDP\
                    messages (or the given connection does not)
        """
        pass

    def receive_sdp_message(self, timeout=None, connection=None):
        """ Receives an SDP message from the board

        :param timeout: Amount of time to wait for the message to arrive in\
                    seconds before a timeout.  If not specified, will wait\
                    indefinitely, or until the selected connection is closed
        :type timeout: int
        :param connection: A specific connection from which to receive the\
                    message.  If not specified, an appropriate connection is\
                    chosen automatically
        :type connection:\
                    :py:class:`spinnman.connections.abstract_sdp_receiver.AbstractSDPReceiver`
        :return: The received message
        :rtype: :py:class:`spinnman.messages.sdp.sdp_message.SDPMessage`
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    communicating with the board
        :raise spinnman.exceptions.SpinnmanUnsupportedOperationException: If\
                    there is no connection that supports reception of\
                    SDP (or the given connection does not)
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If the\
                    message received is not a valid SDP message
        :raise spinnman.exceptions.SpinnmanInvalidParameterException:
                    * If the timeout value is not valid
                    * If the received packet has an invalid parameter
        """
        pass

    def send_scp_message(self, scp_message, connection=None):
        """ Sends an SCP message to the board

        :param scp_message: The SDP message to send
        :type scp_message: :py:class:`spinnman.messages.scp_message.SCPMessage`
        :param connection: A specific connection over which to send the\
                    message.  If not specified, an appropriate connection is\
                    chosen automatically
        :type connection:\
                    :py:class:`spinnman.connections.abstract_scp_sender.AbstractSCPSender`
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    communicating with the board
        :raise spinnman.exceptions.SpinnmanUnsupportedOperationException: If\
                    there is no connection that supports sending SCP\
                    messages (or the given connection does not)
        """
        pass

    def receive_scp_message(self, timeout=None, connection=None):
        """ Receives an SCP message from the board

        :param timeout: Amount of time to wait for the message to arrive in\
                    seconds before a timeout.  If not specified, will wait\
                    indefinitely, or until the selected connection is closed
        :type timeout: int
        :param connection: A specific connection from which to receive the\
                    message.  If not specified, an appropriate connection is\
                    chosen automatically
        :type connection:\
                    :py:class:`spinnman.connections.abstract_scp_receiver.AbstractSCPReceiver`
        :return: The received message
        :rtype: :py:class:`spinnman.messages.scp_message.SCPMessage`
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    communicating with the board
        :raise spinnman.exceptions.SpinnmanUnsupportedOperationException: If\
                    there is no connection that supports reception of\
                    SCP (or the given connection does not)
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If the\
                    message received is not a valid SCP message
        :raise spinnman.exceptions.SpinnmanInvalidParameterException:
                    * If the timeout value is not valid
                    * If the received packet has an invalid parameter
        """
        pass

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
        for connection_queue in self._connection_queues.itervalues():
            connection_queue.stop()

        for connection in self._connections:
            if (close_original_connections
                    or connection not in self._original_connections):
                connection.close()
