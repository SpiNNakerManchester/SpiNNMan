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

from typing import (
    BinaryIO, Collection, Dict, FrozenSet, Iterable,
    List, Optional, Set, Tuple, Union)
from spinn_utilities.abstract_base import abstractmethod
from spinn_utilities.progress_bar import ProgressBar
from spinn_utilities.typing.coords import XY
from spinn_machine import (
    CoreSubsets, Machine, MulticastRoutingEntry, RoutingEntry)
from spinn_machine.tags import AbstractTag, IPTag, ReverseIPTag
from spinnman.connections.abstract_classes import Connection
from spinnman.connections.udp_packet_connections import (
    SCAMPConnection, SDPConnection)
from spinnman.messages.scp.enums import Signal
from spinnman.messages.sdp import SDPMessage
from spinnman.model import (
    CPUInfos, DiagnosticFilter, IOBuffer, RouterDiagnostics,
    VersionInfo)
from spinnman.model.enums import CPUState, UserRegister
from spinnman.processes import MostDirectConnectionSelector


class Transceiver(object):
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
    __slots__ = ()

    @abstractmethod
    def send_sdp_message(self, message: SDPMessage,
                         connection: Optional[SDPConnection] = None) -> None:
        """
        Sends an SDP message using one of the connections.

        :param message: The message to send
        :param connection: An optional connection to use
        """
        # https://github.com/SpiNNakerManchester/SpiNNMan/issues/369
        raise NotImplementedError("abstractmethod")

    @abstractmethod
    def discover_scamp_connections(self) -> None:
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
        raise NotImplementedError("abstractmethod")

    @abstractmethod
    def add_scamp_connections(self, connections: Dict[XY, str]) -> None:
        """
        Check connections to the board and store these for future use.

        .. note::
            An exception will be thrown if no initial connections can be
            found to the board.

        :param connections:
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
        raise NotImplementedError("abstractmethod")

    @abstractmethod
    def get_connections(self) -> Set[Connection]:
        """
        Get the currently known connections to the board, made up of those
        passed in to the transceiver and those that are discovered during
        calls to discover_connections.  No further discovery is done here.

        :return: An iterable of connections known to the transceiver
        """
        # used in unittest only
        raise NotImplementedError("abstractmethod")

    @abstractmethod
    def get_machine_details(self) -> Machine:
        """
        Get the details of the machine made up of chips on a board and how
        they are connected to each other.

        :return: A machine description
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
        raise NotImplementedError("abstractmethod")

    @abstractmethod
    def get_cpu_infos(
            self, core_subsets: Optional[CoreSubsets] = None,
            states: Union[CPUState, Iterable[CPUState], None] = None,
            include: bool = True) -> CPUInfos:
        """
        Get information about the processors on the board.

        :param core_subsets:
            A set of chips and cores from which to get the
            information. If not specified, the information from all of the
            cores on all of the chips on the board are obtained.
        :param states: The state or states to filter on (if any)
        :param include:
            If `True` includes only infos in the requested state(s).
            If `False` includes only infos *not* in the requested state(s).
            Ignored if states is `None`.
        :return: The CPU information for the selected cores and States, or
            all cores/states  if core_subsets/states is not specified
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
        # used by
        # application_finisher
        # chip_provenance_updater
        # emergency_recover_state_from_failure
        raise NotImplementedError("abstractmethod")

    @abstractmethod
    def get_clock_drift(self, x: int, y: int) -> float:
        """
        :param x: The x-coordinate of the chip to get drift for
        :param y: The y-coordinate of the chip to get drift for
        :returns: The current clock drift for this chip
        """
        # used by drift_report
        raise NotImplementedError("abstractmethod")

    @abstractmethod
    def read_user(self, x: int, y: int, p: int, user: UserRegister) -> int:
        """
        Get the contents of the this user register for the given processor.

        .. note::
            Conventionally, user_0 usually holds the address of the table of
            memory regions.

        :param x: X coordinate of the chip
        :param y: Y coordinate of the chip
        :param p: Virtual processor identifier on the chip
        :param user: The user number to read data for
        :returns: Current value on the Machine for this x, y, p, user
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
        raise NotImplementedError("abstractmethod")

    @abstractmethod
    def add_cpu_information_from_core(
            self, cpu_infos: CPUInfos, x: int, y: int, p: int,
            states: Iterable[CPUState]) -> None:
        """
        Adds information about a specific processor on the board to the info

        :param cpu_infos: Info to add data for this core to
        :param x: The x-coordinate of the chip containing the processor
        :param y: The y-coordinate of the chip containing the processor
        :param p: The ID of the processor to get the information about
        :param states:
            If provided will only add the info if in one of the states
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
        # used by emergency_recover_state_from_failure
        raise NotImplementedError("abstractmethod")

    @abstractmethod
    def get_region_base_address(self, x: int, y: int, p: int) -> int:
        """
        Gets the base address of the Region Table

        :param x: The x-coordinate of the chip containing the processor
        :param y: The y-coordinate of the chip containing the processor
        :param p: The ID of the processor to get the address
        :return: The address of the Region table for the selected core
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
        raise NotImplementedError("abstractmethod")

    @abstractmethod
    def get_iobuf(self, core_subsets: Optional[CoreSubsets] = None
                  ) -> Iterable[IOBuffer]:
        """
        Get the contents of the IOBUF buffer for a number of processors.

        :param core_subsets:
            A set of chips and cores from which to get the buffers. If not
            specified, the buffers from all of the cores on all of the chips
            on the board are obtained.
        :return: An iterable of the buffers, which may not be in the order
            of core_subsets
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
        raise NotImplementedError("abstractmethod")

    @abstractmethod
    def get_core_state_count(
            self, app_id: int, state: CPUState,
            xys: Optional[Iterable[Tuple[int, int]]] = None) -> int:
        """
        Get a count of the number of cores which have a given state.

        :param app_id:
            The ID of the application from which to get the count.
        :param state: The state count to get
        :param xys: The chips to query, or None for all
        :return: A count of the cores with the given status
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
        raise NotImplementedError("abstractmethod")

    @abstractmethod
    def execute_flood(
            self, core_subsets: CoreSubsets,
            executable: Union[BinaryIO, bytes, str], app_id: int, *,
            n_bytes: Optional[int] = None, wait: bool = False) -> None:
        """
        Start an executable running on multiple places on the board.  This
        will be optimised based on the selected cores, but it may still
        require a number of communications with the board to execute.

        :param core_subsets:
            Which cores on which chips to start the executable
        :param executable:
            The data that is to be executed. Should be one of the following:
            * An instance of RawIOBase
            * A bytearray
            * A filename of an executable
        :param app_id:
            The ID of the application with which to associate the executable
        :param n_bytes:
            The size of the executable data in bytes. If not specified:

            * If `executable` is an RawIOBase, an error is raised
            * If `executable` is a bytearray, the length of the bytearray will
              be used
            * If `executable` is a str, the length of the file will be used
        :param wait:
            True if the processors should enter a "wait" state on loading
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
        raise NotImplementedError("abstractmethod")

    @abstractmethod
    def read_fpga_register(
            self, fpga_num: int, register: int, board: int = 0) -> int:
        """
        Read a register on a FPGA of a board. The meaning of the
        register's contents will depend on the FPGA's configuration.

        :param fpga_num: FPGA number (0, 1 or 2) to communicate with.
        :param register:
            Register address to read to (will be rounded down to
            the nearest 32-bit word boundary).
        :param board: which board to request the FPGA register from
        :return: the register data
        """
        raise NotImplementedError("abstractmethod")

    @abstractmethod
    def write_fpga_register(self, fpga_num: int, register: int, value: int,
                            board: int = 0) -> None:
        """
        Write a register on a FPGA of a board. The meaning of setting the
        register's contents will depend on the FPGA's configuration.

        :param fpga_num: FPGA number (0, 1 or 2) to communicate with.
        :param register:
            Register address to read to (will be rounded down to
            the nearest 32-bit word boundary).
        :param value: the value to write into the FPGA register
        :param board: which board to write the FPGA register to
        """
        raise NotImplementedError("abstractmethod")

    @abstractmethod
    def read_bmp_version(self, board: int) -> VersionInfo:
        """
        Read the BMP version.

        :param board: which board to request the data from
        :return: the version_info from the BMP
        """
        raise NotImplementedError("abstractmethod")

    @abstractmethod
    def write_memory(
            self, x: int, y: int, base_address: int,
            data: Union[BinaryIO, bytes, int, str], *,
            n_bytes: Optional[int] = None, offset: int = 0, cpu: int = 0,
            get_sum: bool = False) -> Tuple[int, int]:
        """
        Write to the SDRAM on the board.

        :param x:
            The x-coordinate of the chip where the memory is to be written to
        :param y:
            The y-coordinate of the chip where the memory is to be written to
        :param base_address:
            The address in SDRAM where the region of memory is to be written
        :param data: The data to write.  Should be one of the following:

            * An instance of RawIOBase
            * A bytearray/bytes
            * A single integer - will be written in little-endian byte order
            * A string - the filename of a data file
        :param n_bytes:
            The amount of data to be written in bytes.  If not specified:

            * If `data` is an RawIOBase, an error is raised
            * If `data` is a bytearray, the length of the bytearray will be
              used
            * If `data` is an int, 4 will be used
            * If `data` is a str, the length of the file will be used
        :param offset: The offset from which the valid data begins
        :param cpu: The optional CPU to write to
        :param get_sum: whether to return a checksum or 0
        :return: The number of bytes written, the checksum (0 if get_sum=False)
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
        raise NotImplementedError("abstractmethod")

    @abstractmethod
    def write_user(self, x: int, y: int, p: int, user: UserRegister,
                   value: int) -> None:
        """
        Write to the user *N* "register" for the given processor.

        .. note::
            Conventionally, user_0 usually holds the address of the table of
            memory regions.

        :param x: X coordinate of the chip
        :param y: Y coordinate of the chip
        :param p: Virtual processor identifier on the chip
        :param user: The user "register" number of write data for
        :param value: The value to write
        :raise SpinnmanIOException:
            If there is an error communicating with the board
        :raise SpinnmanInvalidPacketException:
            If a packet is received that is not in the valid format
        :raise SpinnmanInvalidParameterException:
            If x, y, p does not identify a valid processor
        :raise SpinnmanUnexpectedResponseCodeException:
            If a response indicates an error during the exchange
        """
        raise NotImplementedError("abstractmethod")

    def write_user_many(
            self, values: List[Tuple[int, int, int, UserRegister, int]],
            description: Optional[str] = None) -> None:
        """ Write to the user *N* "register" for each of the given processors

        :param values:
            List of (x, y, p, register, value) to write
        :param description:
            Optional description of what is being written for progress bar
        :raise SpinnmanIOException:
            If there is an error communicating with the board
        :raise SpinnmanInvalidPacketException:
            If a packet is received that is not in the valid format
        :raise SpinnmanInvalidParameterException:
            If x, y, p does not identify a valid processor
        :raise SpinnmanUnexpectedResponseCodeException:
            If a response indicates an error during the exchange
        """
        raise NotImplementedError("abstractmethod")

    @abstractmethod
    def read_memory(
            self, x: int, y: int, base_address: int, length: int,
            cpu: int = 0) -> bytearray:
        """
        Read some areas of memory (usually SDRAM) from the board.

        :param x:
            The x-coordinate of the chip where the memory is to be read from
        :param y:
            The y-coordinate of the chip where the memory is to be read from
        :param base_address:
            The address in SDRAM where the region of memory to be read starts
        :param length: The length of the data to be read in bytes
        :param cpu:
            the core ID used to read the memory of; should usually be 0 when
            reading from SDRAM, but may be other values when reading from DTCM.
        :return: A bytearray of data read
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
        raise NotImplementedError("abstractmethod")

    @abstractmethod
    def read_word(
            self, x: int, y: int, base_address: int, cpu: int = 0) -> int:
        """
        Read a word (usually of SDRAM) from the board.

        :param x:
            The x-coordinate of the chip where the word is to be read from
        :param y:
            The y-coordinate of the chip where the word is to be read from
        :param base_address:
            The address (usually in SDRAM) where the word to be read starts
        :param cpu:
            the core ID used to read the word; should usually be 0 when reading
            from SDRAM, but may be other values when reading from DTCM.
        :return: The unsigned integer value at ``base_address``
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
        raise NotImplementedError("abstractmethod")

    @abstractmethod
    def stop_application(self, app_id: int) -> None:
        """
        Sends a stop request for an app_id.

        :param app_id: The ID of the application to send to
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
        raise NotImplementedError("abstractmethod")

    @abstractmethod
    def wait_for_cores_to_be_in_state(
            self, all_core_subsets: CoreSubsets, app_id: int,
            cpu_states: Union[CPUState, Iterable[CPUState]], *,
            timeout: Optional[float] = None,
            time_between_polls: float = 0.1,
            error_states: FrozenSet[CPUState] = frozenset((
                CPUState.RUN_TIME_EXCEPTION, CPUState.WATCHDOG)),
            counts_between_full_check: int = 100,
            progress_bar: Optional[ProgressBar] = None) -> None:
        """
        Waits for the specified cores running the given application to be
        in some target state or states. Handles failures.

        :param all_core_subsets:
            the cores to check are in a given sync state
        :param app_id: the application ID that being used by the simulation
        :param cpu_states:
            The expected states once the applications are ready; success is
            when each application is in one of these states
        :param timeout:
            The amount of time to wait in seconds for the cores to reach one
            of the states
        :param time_between_polls: Time between checking the state
        :param error_states:
            Set of states that the application can be in that indicate an
            error, and so should raise an exception
        :param counts_between_full_check:
            The number of times to use the count signal before instead using
            the full CPU state check
        :param progress_bar: Possible progress bar to update.
        :raise SpinnmanTimeoutException:
            If a timeout is specified and exceeded.
        """
        raise NotImplementedError("abstractmethod")

    @abstractmethod
    def send_signal(self, app_id: int, signal: Signal) -> None:
        """
        Send a signal to an application.

        :param app_id: The ID of the application to send to
        :param signal: The signal to send
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
        raise NotImplementedError("abstractmethod")

    @abstractmethod
    def set_ip_tag(self, ip_tag: IPTag, use_sender: bool = False) -> None:
        """
        Set up an IP tag.

        :param ip_tag: The tag to set up.

            .. note::
                `board_address` can be `None`, in which case, the tag will be
                assigned to all boards.
        :param use_sender:
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
        raise NotImplementedError("abstractmethod")

    @abstractmethod
    def set_reverse_ip_tag(self, reverse_ip_tag: ReverseIPTag) -> None:
        """
        Set up a reverse IP tag.

        :param reverse_ip_tag:
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
        raise NotImplementedError("abstractmethod")

    @abstractmethod
    def clear_ip_tag(
            self, tag: int, board_address: Optional[str] = None) -> None:
        """
        Clear the setting of an IP tag.

        :param tag: The tag ID
        :param board_address:
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
        raise NotImplementedError("abstractmethod")

    @abstractmethod
    def get_tags(self, connection: Optional[SCAMPConnection] = None
                 ) -> Iterable[AbstractTag]:
        """
        Get the current set of tags that have been set on the board.

        :param connection:
            Connection from which the tags should be received.
            If not specified, all AbstractSCPConnection connections will be
            queried and the response will be combined.
        :return: An iterable of tags
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
        raise NotImplementedError("abstractmethod")

    @abstractmethod
    def malloc_sdram(
            self, x: int, y: int, size: int, app_id: int, tag: int = 0) -> int:
        """
        Allocates a chunk of SDRAM on a chip on the machine.

        :param x: The x-coordinate of the chip onto which to ask for memory
        :param y: The y-coordinate of the chip onto which to ask for memory
        :param size: the amount of memory to allocate in bytes
        :param app_id: The ID of the application with which to associate
            the routes.  If not specified, defaults to 0.
        :param tag: the tag for the SDRAM, a 8-bit (chip-wide) tag that can
            be looked up by a SpiNNaker application to discover the address of
            the allocated block. If `0` then no tag is applied.
        :return: the base address of the allocated memory
        """
        raise NotImplementedError("abstractmethod")

    @abstractmethod
    def malloc_sdram_multi(
            self, allocations: List[Tuple[int, int, int, int, int]]
            ) -> List[int]:
        """
        Allocate space in the SDRAM space for multiple chips

        :param allocations:
            List of (x, y, size, app_id, tag)
        :return: List of base addresses that match each of the requests
        """
        raise NotImplementedError("abstractmethod")

    @abstractmethod
    def load_multicast_routes(
            self, x: int, y: int, routes: Collection[MulticastRoutingEntry],
            app_id: int) -> None:
        """
        Load a set of multicast routes on to a chip.

        :param x:
            The x-coordinate of the chip onto which to load the routes
        :param y:
            The y-coordinate of the chip onto which to load the routes
        :param routes:
            An iterable of multicast routes to load
        :param app_id: The ID of the application with which to associate
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
        raise NotImplementedError("abstractmethod")

    @abstractmethod
    def load_fixed_route(self, x: int, y: int, fixed_route: RoutingEntry,
                         app_id: int) -> None:
        """
        Loads a fixed route routing table entry onto a chip's router.

        :param x:
            The x-coordinate of the chip onto which to load the routes
        :param y:
            The y-coordinate of the chip onto which to load the routes
        :param fixed_route:
            the route for the fixed route entry on this chip
        :param app_id: The ID of the application with which to associate
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
        raise NotImplementedError("abstractmethod")

    @abstractmethod
    def read_fixed_route(self, x: int, y: int, app_id: int) -> RoutingEntry:
        """
        Reads a fixed route routing table entry from a chip's router.

        :param x:
            The x-coordinate of the chip onto which to load the routes
        :param y:
            The y-coordinate of the chip onto which to load the routes
        :param app_id:
            The ID of the application with which to associate the
            routes.  If not specified, defaults to 0.
        :return: the route as a fixed route entry
        """
        raise NotImplementedError("abstractmethod")

    @abstractmethod
    def get_multicast_routes(
            self, x: int, y: int,
            app_id: Optional[int] = None) -> List[MulticastRoutingEntry]:
        """
        Get the current multicast routes set up on a chip.

        :param x:
            The x-coordinate of the chip from which to get the routes
        :param y:
            The y-coordinate of the chip from which to get the routes
        :param app_id:
            The ID of the application to filter the routes for. If
            not specified, will return all routes
        :return: An iterable of multicast routes
        :raise SpinnmanIOException:
            If there is an error communicating with the board
        :raise SpinnmanInvalidPacketException:
            If a packet is received that is not in the valid format
        :raise SpinnmanInvalidParameterException:
            If a packet is received that has invalid parameters
        :raise SpinnmanUnexpectedResponseCodeException:
            If a response indicates an error during the exchange
        """
        raise NotImplementedError("abstractmethod")

    @abstractmethod
    def clear_multicast_routes(self, xy: Optional[XY] = None) -> None:
        """
        Remove all the multicast routes on a chip.

        :param xy:
            Optional chip to clear the multicast routes on. If not
            specified, all chips will have their multicast routes cleared.
        :raise SpinnmanIOException:
            If there is an error communicating with the board
        :raise SpinnmanInvalidPacketException:
            If a packet is received that is not in the valid format
        :raise SpinnmanInvalidParameterException:
            If a packet is received that has invalid parameters
        :raise SpinnmanUnexpectedResponseCodeException:
            If a response indicates an error during the exchange
        """
        raise NotImplementedError("abstractmethod")

    @abstractmethod
    def get_router_diagnostics(self, x: int, y: int) -> RouterDiagnostics:
        """
        Get router diagnostic information from a chip.

        :param x:
            The x-coordinate of the chip from which to get the information
        :param y:
            The y-coordinate of the chip from which to get the information
        :return: The router diagnostic information
        :raise SpinnmanIOException:
            If there is an error communicating with the board
        :raise SpinnmanInvalidPacketException:
            If a packet is received that is not in the valid format
        :raise SpinnmanInvalidParameterException:
            If a packet is received that has invalid parameters
        :raise SpinnmanUnexpectedResponseCodeException:
            If a response indicates an error during the exchange
        """
        raise NotImplementedError("abstractmethod")

    @abstractmethod
    def get_scamp_connection_selector(self) -> MostDirectConnectionSelector:
        """
        :returns: the most direct scamp connections
         """
        raise NotImplementedError("abstractmethod")

    @abstractmethod
    def set_router_diagnostic_filter(
            self, x: int, y: int, position: int,
            diagnostic_filter: DiagnosticFilter) -> None:
        """
        Sets a router diagnostic filter in a router.

        :param x:
            The X address of the router in which this filter is being set.
        :param y:
            The Y address of the router in which this filter is being set.
        :param position:
            The position in the list of filters where this filter is to be
            added.
        :param diagnostic_filter:
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
        raise NotImplementedError("abstractmethod")

    @abstractmethod
    def clear_router_diagnostic_counters(
            self, xy: Optional[XY] = None) -> None:
        """
        Clear router diagnostic information on a chip.

        :param xy:
            The optional XY coordinate of the chip to clear the counters on.
            If not specified, all chips will have their counters cleared.
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
        raise NotImplementedError("abstractmethod")

    @abstractmethod
    def close(self) -> None:
        """ Close the transceiver and any threads that are running. """
        raise NotImplementedError("abstractmethod")

    @abstractmethod
    def control_sync(self, do_sync: bool) -> None:
        """
        Control the synchronisation of the chips.

        :param do_sync: Whether to synchronise or not
        """
        raise NotImplementedError("abstractmethod")

    @abstractmethod
    def update_provenance_and_exit(self, x: int, y: int, p: int) -> None:
        """
        Sends a command to update provenance and exit

        :param x: The x-coordinate of the core
        :param y: The y-coordinate of the core
        :param p: The processor on the core
        """
        raise NotImplementedError("abstractmethod")

    @abstractmethod
    def send_chip_update_provenance_and_exit(
            self, x: int, y: int, p: int) -> None:
        """
        Sends a signal to update the provenance and exit

        :param x: X coordinate of the Chip
        :param y: Y coordinate of the Chip
        :param p: core number on the Chip
        """
        raise NotImplementedError("abstractmethod")

    @abstractmethod
    def reset_routing(self) -> None:
        """
        Reset routing tables and set up some default diagnostics

        """
        raise NotImplementedError("abstractmethod")

    @abstractmethod
    def ensure_board_is_ready(self) -> None:
        """
        Ensure that the board is ready to interact with this version of the
        transceiver. Boots the board if not already booted and verifies that
        the version of SCAMP running is compatible with this transceiver.

        :raise SpinnmanIOException:
            * If there is a problem booting the board
            * If the version of software on the board is not compatible with
              this transceiver
        """
        raise NotImplementedError("abstractmethod")
