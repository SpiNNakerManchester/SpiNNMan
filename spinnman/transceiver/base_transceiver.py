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
from collections import defaultdict
import io
import os
import random
import struct
from contextlib import contextmanager, suppress
import logging
import socket
from threading import Condition
import time
from spinn_utilities.abstract_base import (
    AbstractBase, abstractproperty)
from spinn_utilities.config_holder import get_config_bool
from spinn_utilities.log import FormatAdapter
from spinn_utilities.overrides import overrides
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
from spinnman.utilities.utility_functions import get_vcpu_address
from spinnman.transceiver.transceiver import Transceiver
from spinnman.transceiver.extendable_transceiver import ExtendableTransceiver

logger = FormatAdapter(logging.getLogger(__name__))

_SCAMP_NAME = "SC&MP"
_SCAMP_VERSION = (3, 0, 1)

_BMP_NAME = "BC&MP"
_BMP_MAJOR_VERSIONS = [1, 2]

_CONNECTION_CHECK_RETRIES = 3
INITIAL_FIND_SCAMP_RETRIES_COUNT = 3

_TWO_BYTES = struct.Struct("<BB")
_FOUR_BYTES = struct.Struct("<BBBB")
_ONE_WORD = struct.Struct("<I")
_ONE_LONG = struct.Struct("<Q")
_EXECUTABLE_ADDRESS = 0x67800000


class BaseTransceiver(ExtendableTransceiver, metaclass=AbstractBase):
    """
    A base for all the code shared by all Version of the Transciever.

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
        "_width"]

    def __init__(self, connections=None):
        """
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
        super().__init__()

        # Place to keep the current machine
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

        # A lock against single chip executions (entry is (x, y))
        # The condition should be acquired before the locks are
        # checked or updated
        # The write lock condition should also be acquired to avoid a flood
        # fill during an individual chip execute
        self._chip_execute_locks = defaultdict(Condition)
        self._chip_execute_lock_condition = Condition()
        self._n_chip_execute_locks = 0

        # build connection selectors for the processes.
        self._bmp_selector = None
        self._scamp_connection_selector = \
            self.__identify_connections(connections)

        # Check that the BMP connections are valid
        self.__check_bmp_connection()

        self._machine_off = False

    @property
    @overrides(ExtendableTransceiver.bmp_selector)
    def bmp_selector(self):
        return self._bmp_selector

    @property
    @overrides(ExtendableTransceiver.scamp_connection_selector)
    def scamp_connection_selector(self):
        return self._scamp_connection_selector

    @property
    @overrides(ExtendableTransceiver.bmp_connection)
    def bmp_connection(self):
        return self._bmp_connection

    @overrides(Transceiver.where_is_xy)
    def where_is_xy(self, x, y):
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

    @overrides(Transceiver.send_sdp_message)
    def send_sdp_message(self, message, connection=None):
        if connection is None:
            connection_to_use = self._scamp_connections[random.randint(
                0, len(self._scamp_connections) - 1)]
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

    @overrides(Transceiver.discover_scamp_connections)
    def discover_scamp_connections(self):
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

    @overrides(Transceiver.add_scamp_connections)
    def add_scamp_connections(self, connections):
        for ((x, y), ip_address) in connections.items():
            self._check_and_add_scamp_connections(x, y, ip_address)
        self._scamp_connection_selector = MostDirectConnectionSelector(
            self._scamp_connections)

    @overrides(Transceiver.get_connections)
    def get_connections(self):
        return self._all_connections

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

    @overrides(Transceiver.get_machine_details)
    def get_machine_details(self):
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

    @abstractproperty
    def boot_led_0_value(self):
        """
        The Values to be set in SpinnakerBootMessages for led_0

        :rtype int:
        """

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
        if extra_boot_values is None:
            extra_boot_values = dict()
        if SystemVariableDefinition.led_0 not in extra_boot_values:
            extra_boot_values[SystemVariableDefinition.led_0] = \
                self.boot_led_0_value
        boot_messages = SpinnakerBootMessages(
            extra_boot_values=extra_boot_values)
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

    @overrides(Transceiver.ensure_board_is_ready)
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

    @overrides(Transceiver.get_cpu_infos)
    def get_cpu_infos(
            self, core_subsets=None, states=None, include=True):
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

    @overrides(Transceiver.get_clock_drift)
    def get_clock_drift(self, x, y):
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

    @overrides(Transceiver.read_user)
    def read_user(self, x, y, p, user):
        addr = self.__get_user_register_address_from_core(p, user)
        return self.read_word(x, y, addr)

    @overrides(Transceiver.get_cpu_information_from_core)
    def get_cpu_information_from_core(self, x, y, p):
        core_subsets = CoreSubsets()
        core_subsets.add_processor(x, y, p)
        cpu_infos = self.get_cpu_infos(core_subsets)
        return cpu_infos.get_cpu_info(x, y, p)

    @overrides(Transceiver.get_iobuf)
    def get_iobuf(self, core_subsets=None):
        # making the assumption that all chips have the same iobuf size.
        if self._iobuf_size is None:
            self._iobuf_size = self._get_sv_data(
                AbstractSCPRequest.DEFAULT_DEST_X_COORD,
                AbstractSCPRequest.DEFAULT_DEST_Y_COORD,
                SystemVariableDefinition.iobuf_size)

        # read iobuf from machine
        process = ReadIOBufProcess(self._scamp_connection_selector)
        return process.read_iobuf(self._iobuf_size, core_subsets)

    @overrides(Transceiver.get_core_state_count)
    def get_core_state_count(self, app_id, state):
        process = SendSingleCommandProcess(self._scamp_connection_selector)
        response = process.execute(CountState(app_id, state))
        return response.count  # pylint: disable=no-member

    @contextmanager
    def _flood_execute_lock(self):
        """
        Get a lock for executing a flood fill of an executable.
        """
        # Get the execute lock all together, so nothing can access it
        with self._chip_execute_lock_condition:
            # Wait until nothing is executing
            self._chip_execute_lock_condition.wait_for(
                lambda: self._n_chip_execute_locks < 1)
            yield self._chip_execute_lock_condition

    @overrides(Transceiver.execute_flood)
    def execute_flood(
            self, core_subsets, executable, app_id, n_bytes=None, wait=False,
            is_filename=False):
        # Lock against other executable's
        with self._flood_execute_lock():
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

    @overrides(Transceiver.power_on)
    def power_on(self, boards=0):
        self._power(PowerCommand.POWER_ON, boards)

    @overrides(Transceiver.power_off_machine)
    def power_off_machine(self):
        if self._bmp_connection is None:
            logger.warning("No BMP connections, so can't power off")
            return False
        logger.info("Turning off machine")
        self.power_off(self._bmp_connection)
        return True

    @overrides(Transceiver.power_off)
    def power_off(self, boards=0):
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

    @overrides(Transceiver.read_fpga_register)
    def read_fpga_register(
            self, fpga_num, register, board=0):
        process = SendSingleCommandProcess(self._bmp_selector, timeout=1.0)
        response = process.execute(
            ReadFPGARegister(fpga_num, register, board))
        return response.fpga_register  # pylint: disable=no-member

    @overrides(Transceiver.write_fpga_register)
    def write_fpga_register(self, fpga_num, register, value, board=0):
        process = SendSingleCommandProcess(self._bmp_selector)
        process.execute(
            WriteFPGARegister(fpga_num, register, value, board))

    @overrides(Transceiver.read_bmp_version)
    def read_bmp_version(self, board):
        process = SendSingleCommandProcess(self._bmp_selector)
        response = process.execute(BMPGetVersion(board))
        return response.version_info  # pylint: disable=no-member

    @overrides(Transceiver.write_memory)
    def write_memory(self, x, y, base_address, data, n_bytes=None, offset=0,
                     cpu=0, is_filename=False, get_sum=False):
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

    @overrides(Transceiver.write_user)
    def write_user(self, x, y, p, user, value):
        addr = self.__get_user_register_address_from_core(p, user)
        self.write_memory(x, y, addr, int(value))

    @overrides(Transceiver.read_memory)
    def read_memory(self, x, y, base_address, length, cpu=0):
        try:
            process = ReadMemoryProcess(self._scamp_connection_selector)
            return process.read_memory(x, y, cpu, base_address, length)
        except Exception:
            logger.info(self.where_is_xy(x, y))
            raise

    @overrides(Transceiver.read_word)
    def read_word(self, x, y, base_address, cpu=0):
        try:
            process = ReadMemoryProcess(self._scamp_connection_selector)
            data = process.read_memory(x, y, cpu, base_address, _ONE_WORD.size)
            (value, ) = _ONE_WORD.unpack(data)
            return value
        except Exception:
            logger.info(self.where_is_xy(x, y))
            raise

    @overrides(Transceiver.stop_application)
    def stop_application(self, app_id):
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
            logger.info(self.where_is_xy(x, y))

    @overrides(Transceiver.wait_for_cores_to_be_in_state)
    def wait_for_cores_to_be_in_state(
            self, all_core_subsets, app_id, cpu_states, timeout=None,
            time_between_polls=0.1,
            error_states=frozenset({
                CPUState.RUN_TIME_EXCEPTION, CPUState.WATCHDOG}),
            counts_between_full_check=100, progress_bar=None):
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

    @overrides(Transceiver.send_signal)
    def send_signal(self, app_id, signal):
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

    @overrides(Transceiver.set_ip_tag)
    def set_ip_tag(self, ip_tag, use_sender=False):
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

    @overrides(Transceiver.set_reverse_ip_tag)
    def set_reverse_ip_tag(self, reverse_ip_tag):
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

    @overrides(Transceiver.clear_ip_tag)
    def clear_ip_tag(self, tag, board_address=None):
        for conn in self.__get_connection_list(board_address=board_address):
            process = SendSingleCommandProcess(self._scamp_connection_selector)
            process.execute(IPTagClear(conn.chip_x, conn.chip_y, tag))

    @overrides(Transceiver.get_tags)
    def get_tags(self, connection=None):
        all_tags = list()
        for conn in self.__get_connection_list(connection):
            process = GetTagsProcess(self._scamp_connection_selector)
            all_tags.extend(process.get_tags(conn))
        return all_tags

    @overrides(Transceiver.malloc_sdram)
    def malloc_sdram(self, x, y, size, app_id, tag=None):
        try:
            process = MallocSDRAMProcess(self._scamp_connection_selector)
            process.malloc_sdram(x, y, size, app_id, tag)
            return process.base_address
        except Exception:
            logger.info(self.where_is_xy(x, y))
            raise

    @overrides(Transceiver.load_multicast_routes)
    def load_multicast_routes(self, x, y, routes, app_id):
        try:
            process = LoadMultiCastRoutesProcess(
                self._scamp_connection_selector)
            process.load_routes(x, y, routes, app_id)
        except Exception:
            logger.info(self.where_is_xy(x, y))
            raise

    @overrides(Transceiver.load_fixed_route)
    def load_fixed_route(self, x, y, fixed_route, app_id):
        try:
            process = LoadFixedRouteRoutingEntryProcess(
                self._scamp_connection_selector)
            process.load_fixed_route(x, y, fixed_route, app_id)
        except Exception:
            logger.info(self.where_is_xy(x, y))
            raise

    @overrides(Transceiver.read_fixed_route)
    def read_fixed_route(self, x, y, app_id):
        try:
            process = ReadFixedRouteRoutingEntryProcess(
                self._scamp_connection_selector)
            return process.read_fixed_route(x, y, app_id)
        except Exception:
            logger.info(self.where_is_xy(x, y))
            raise

    @overrides(Transceiver.get_multicast_routes)
    def get_multicast_routes(self, x, y, app_id=None):
        try:
            base_address = self._get_sv_data(
                x, y, SystemVariableDefinition.router_table_copy_address)
            process = GetMultiCastRoutesProcess(
                self._scamp_connection_selector, app_id)
            return process.get_routes(x, y, base_address)
        except Exception:
            logger.info(self.where_is_xy(x, y))
            raise

    @overrides(Transceiver.clear_multicast_routes)
    def clear_multicast_routes(self, x, y):
        try:
            process = SendSingleCommandProcess(self._scamp_connection_selector)
            process.execute(RouterClear(x, y))
        except Exception:
            logger.info(self.where_is_xy(x, y))
            raise

    @overrides(Transceiver.get_router_diagnostics)
    def get_router_diagnostics(self, x, y):
        try:
            process = ReadRouterDiagnosticsProcess(
                self._scamp_connection_selector)
            return process.get_router_diagnostics(x, y)
        except Exception:
            logger.info(self.where_is_xy(x, y))
            raise

    @overrides(Transceiver.set_router_diagnostic_filter)
    def set_router_diagnostic_filter(self, x, y, position, diagnostic_filter):
        try:
            self.__set_router_diagnostic_filter(
                x, y, position, diagnostic_filter)
        except Exception:
            logger.info(self.where_is_xy(x, y))
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
            logger.info(self.where_is_xy(x, y))
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
