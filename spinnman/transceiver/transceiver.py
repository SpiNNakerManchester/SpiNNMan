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

from spinn_utilities.abstract_base import (
    AbstractBase, abstractmethod)
from spinn_utilities.abstract_context_manager import AbstractContextManager
from spinnman.model.enums import CPUState


class Transceiver(AbstractContextManager, metaclass=AbstractBase):
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
    __slots__ = []

    @abstractmethod
    def send_sdp_message(self, message, connection=None):
        """
        Sends an SDP message using one of the connections.

        :param SDPMessage message: The message to send
        :param SDPConnection connection: An optional connection to use
        """
        # _ChipProvenanceUpdater._send_chip_update_provenance_and_exit
        # https://github.com/SpiNNakerManchester/SpiNNMan/pull/357
        # DataSpeedUpPacketGatherMachineVertex.
        #      _determine_and_retransmit_missing_seq_nums
        # https://github.com/SpiNNakerManchester/SpiNNFrontEndCommon/pull/1102

    @abstractmethod
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
        # Used directly after Transceiver init
        # Not called if add_scamp_connections is called
        # Not called by SpallocJobController

    @abstractmethod
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
        # Use on a spalloc created Transceiver

    @abstractmethod
    def get_connections(self):
        """
        Get the currently known connections to the board, made up of those
        passed in to the transceiver and those that are discovered during
        calls to discover_connections.  No further discovery is done here.

        :return: An iterable of connections known to the transceiver
        :rtype: set(Connection)
        """
        # used in unittest only

    @abstractmethod
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
        # used by machine_generator

    @abstractmethod
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
        # See https://github.com/SpiNNakerManchester/SpiNNMan/pull/358
        # used by
        # ASB.__recover_from_error
        # application_finisher
        # chip_provenance_updater
        # emergency_recover_state_from_failure

    @abstractmethod
    def get_clock_drift(self, x, y):
        """
        Get the clock drift
        :param int x: The x-coordinate of the chip to get drift for
        :param int y: The y-coordinate of the chip to get drift for
        """
        # used by drift_report

    @abstractmethod
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
        # used by pair_compression and others during _check_for_success
        # used by memory_map_on_host_chip_report._get_region_table_addr
        #   https://github.com/SpiNNakerManchester/SpiNNFrontEndCommon/pull/1104
        # used by DataSpeedUpPacketGatherMachineVertex
        #    and ExtraMonitorSupportMachineVertex
        #    to .update_transaction_id_from_machine

    @abstractmethod
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
        # see https://github.com/SpiNNakerManchester/SpiNNMan/pull/358

    @abstractmethod
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
        # Used by IOBufExtractor

    @abstractmethod
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

    @abstractmethod
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
        # Used by load_app_images, load_sys_images and
        # run_system_application._load_application

    @abstractmethod
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

    @abstractmethod
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

    @abstractmethod
    def read_bmp_version(self, board):
        """
        Read the BMP version.

        :param int board: which board to request the data from
        :return: the sver from the BMP
        """

    @abstractmethod
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

    @abstractmethod
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

    @abstractmethod
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

    @abstractmethod
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

    @abstractmethod
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

    @abstractmethod
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

    @abstractmethod
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
        # Known usages are to send Signal START, SYNC0 and SYNC1

    @abstractmethod
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

    @abstractmethod
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

    @abstractmethod
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

    @abstractmethod
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

    @abstractmethod
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

    @abstractmethod
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

    @abstractmethod
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

    @abstractmethod
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

    @abstractmethod
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

    @abstractmethod
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

    @abstractmethod
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

    @abstractmethod
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

    @abstractmethod
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

    @abstractmethod
    def close(self):
        """
        Close the transceiver and any threads that are running.
        """

    @abstractmethod
    def control_sync(self, do_sync):
        """
        Control the synchronisation of the chips.

        :param bool do_sync: Whether to synchronise or not
        """

    @abstractmethod
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

    @abstractmethod
    def where_is_xy(self, x, y):
        """
        Attempts to get where_is_x_y info from the machine

        If no machine will do its best.

        :param int x:
        :param int y:
        :rtype: str
        """
