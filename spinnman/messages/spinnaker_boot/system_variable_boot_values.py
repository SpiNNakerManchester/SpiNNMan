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

from collections import namedtuple
import struct
from enum import Enum

_SYSTEM_VARIABLES_BOOT_SIZE = 128


class _DataType(Enum):
    """
    Enum for data types.
    """
    BYTE = (1, "<B")
    SHORT = (2, "<H")
    INT = (4, "<I")
    LONG = (8, "<Q")
    BYTE_ARRAY = (16, "s")

    def __new__(cls, value, struct_code, doc=""):
        # pylint: disable=protected-access, unused-argument
        obj = object.__new__(cls)
        obj._value_ = value
        obj._struct_code = struct_code
        return obj

    def __init__(self, value, struct_code, doc=""):
        self._value_ = value
        self._struct_code = struct_code
        self.__doc__ = doc

    @property
    def struct_code(self):
        return self._struct_code

    @property
    def is_byte_array(self):
        # can't use BYTE_ARRAY.value directly here
        return self._value_ == 16


class _Definition(namedtuple("_Definition",
                             "offset, data_type, default, array_size, doc")):
    """
    helper class that contains a definition for a variable.
    """

    def __new__(cls, data_type, offset, default=0, array_size=None, doc=""):
        # pylint: disable=too-many-arguments
        return super().__new__(
            cls, offset, data_type, default, array_size, doc)


class SystemVariableDefinition(Enum):
    """
    Defines the system variables available.
    """

    y = _Definition(
        _DataType.BYTE, offset=0, doc="The y-coordinate of the chip")
    x = _Definition(
        _DataType.BYTE, offset=0x01, doc="The x-coordinate of the chip")
    y_size = _Definition(
        _DataType.BYTE, offset=0x02,
        doc="The number of chips in the y-dimension")
    x_size = _Definition(
        _DataType.BYTE, offset=0x03,
        doc="The number of chips in the x-dimension")
    debug_y = _Definition(
        _DataType.BYTE, offset=0x04,
        doc="The y-coordinate of the chip to send debug messages to")
    debug_x = _Definition(
        _DataType.BYTE, offset=0x05,
        doc="The x-coordinate of the chip to send debug messages to")
    is_peer_to_peer_available = _Definition(
        _DataType.BYTE, offset=0x06,
        doc="Indicates if peer-to-peer is working on the chip")
    nearest_neighbour_last_id = _Definition(
        _DataType.BYTE, offset=0x07,
        doc="The last ID used in nearest neighbour transaction")
    nearest_ethernet_y = _Definition(
        _DataType.BYTE, offset=0x08,
        doc="The x-coordinate of the nearest chip with Ethernet")
    nearest_ethernet_x = _Definition(
        _DataType.BYTE, offset=0x09,
        doc="The y-coordinate of the nearest chip with Ethernet")
    hardware_version = _Definition(
        _DataType.BYTE, offset=0x0a,
        doc="The version of the hardware in use")
    is_ethernet_available = _Definition(
        _DataType.BYTE, offset=0x0b,
        doc="Indicates if Ethernet is available on this chip")
    p2p_b_repeats = _Definition(
        _DataType.BYTE, offset=0x0c, default=4,
        doc="Number of times to send out P2PB packets")
    log_peer_to_peer_sequence_length = _Definition(
        _DataType.BYTE, offset=0x0d, default=4,
        doc="Log (base 2) of the peer-to-peer sequence length")
    clock_divisor = _Definition(
        _DataType.BYTE, offset=0x0e, default=0x33,
        doc="The clock divisors for system & router clocks")
    time_phase_scale = _Definition(
        _DataType.BYTE, offset=0x0f,
        doc="The time-phase scaling factor")
    clock_milliseconds = _Definition(
        _DataType.LONG, offset=0x10,
        doc="The time since startup in milliseconds")
    time_milliseconds = _Definition(
        _DataType.SHORT, offset=0x18,
        doc="The number of milliseconds in the current second")
    ltpc_period = _Definition(
        _DataType.SHORT, offset=0x1a)
    unix_timestamp = _Definition(
        _DataType.INT, offset=0x1c,
        doc="The time in seconds since midnight, 1st January 1970")
    router_time_phase_timer = _Definition(
        _DataType.INT, offset=0x20,
        doc="The router time-phase timer")
    cpu_clock_mhz = _Definition(
        _DataType.SHORT, offset=0x24, default=200,
        doc="The CPU clock frequency in MHz")
    sdram_clock_frequency_mhz = _Definition(
        _DataType.SHORT, offset=0x26, default=130,
        doc="The SDRAM clock frequency in MHz")
    nearest_neighbour_forward = _Definition(
        _DataType.BYTE, offset=0x28, default=0x3F,
        doc="Nearest-Neighbour forward parameter")
    nearest_neighbour_retry = _Definition(
        _DataType.BYTE, offset=0x29,
        doc="Nearest-Neighbour retry parameter")
    link_peek_timeout_microseconds = _Definition(
        _DataType.BYTE, offset=0x2a, default=100,
        doc="The link peek/poke timeout in microseconds")
    led_half_period_10_ms = _Definition(
        _DataType.BYTE, offset=0x2b, default=1,
        doc="The LED half-period in 10 ms units, or 1 to show load")
    netinit_bc_wait_time = _Definition(
        _DataType.BYTE, offset=0x2c, default=50,
        doc="The time to wait after last BC during network initialisation"
            " in 10 ms units")
    netinit_phase = _Definition(
        _DataType.BYTE, offset=0x2d,
        doc="The phase of boot process (see enum netinit_phase_e)")
    p2p_root_y = _Definition(
        _DataType.BYTE, offset=0x2e,
        doc="The y-coordinate of the chip from which the system was booted")
    p2p_root_x = _Definition(
        _DataType.BYTE, offset=0x2f,
        doc="The x-coordinate of the chip from which the system was booted")
    led_0 = _Definition(
        _DataType.INT, offset=0x30, default=0x1,
        doc="The first part of the LED definitions")
    led_1 = _Definition(
        _DataType.INT, offset=0x34,
        doc="The last part of the LED definitions")
    clock_drift = _Definition(
        _DataType.INT, offset=0x38,
        doc="The clock drift")
    random_seed = _Definition(
        _DataType.INT, offset=0x3c,
        doc="The random seed")
    is_root_chip = _Definition(
        _DataType.BYTE, offset=0x40,
        doc="Indicates if this is the root chip")
    n_shared_message_buffers = _Definition(
        _DataType.BYTE, offset=0x41, default=7,
        doc="The number of shared message buffers")
    nearest_neighbour_delay_us = _Definition(
        _DataType.BYTE, offset=0x42, default=20,
        doc="The delay between nearest-neighbour packets in microseconds")
    software_watchdog_count = _Definition(
        _DataType.BYTE, offset=0x43,
        doc="The number of watch dog timeouts before an error is raised")
    padding_2 = _Definition(
        _DataType.INT, offset=0x44,
        doc="A word of padding")
    system_ram_heap_address = _Definition(
        _DataType.INT, offset=0x48, default=1024,
        doc="The base address of the system SDRAM heap")
    sdram_heap_address = _Definition(
        _DataType.INT, offset=0x4c, default=0,
        doc="The base address of the user SDRAM heap")
    iobuf_size = _Definition(
        _DataType.INT, offset=0x50, default=16384,
        doc="The size of the iobuf buffer in bytes")
    system_sdram_bytes = _Definition(
        _DataType.INT, offset=0x54, default=8388608,
        doc="The size of the system SDRAM in bytes")
    system_buffer_words = _Definition(
        _DataType.INT, offset=0x58, default=32768,
        doc="The size of the system buffer in words")
    boot_signature = _Definition(
        _DataType.INT, offset=0x5c,
        doc="The boot signature")
    nearest_neighbour_memory_pointer = _Definition(
        _DataType.INT, offset=0x60,
        doc="The memory pointer for nearest neighbour global operations")
    lock = _Definition(
        _DataType.BYTE, offset=0x64,
        doc="The lock")
    links_available = _Definition(
        _DataType.BYTE, offset=0x65, default=0x3f,
        doc="Bit mask (6 bits) of links enabled")
    last_biff_id = _Definition(
        _DataType.BYTE, offset=0x66,
        doc="Last ID used in BIFF packet")
    board_test_flags = _Definition(
        _DataType.BYTE, offset=0x67,
        doc="Board testing flags")
    shared_message_first_free_address = _Definition(
        _DataType.INT, offset=0x68,
        doc="Pointer to the first free shared message buffer")
    shared_message_count_in_use = _Definition(
        _DataType.SHORT, offset=0x6c,
        doc="The number of shared message buffers in use")
    shared_message_maximum_used = _Definition(
        _DataType.SHORT, offset=0x6e,
        doc="The maximum number of shared message buffers used")
    user_temp_0 = _Definition(
        _DataType.INT, offset=0x70,
        doc="The first user variable")
    user_temp_1 = _Definition(
        _DataType.INT, offset=0x74,
        doc="The second user variable")
    user_temp_2 = _Definition(
        _DataType.INT, offset=0x78,
        doc="The third user variable")
    user_temp_4 = _Definition(
        _DataType.INT, offset=0x7c,
        doc="The fourth user variable")
    status_map = _Definition(
        _DataType.BYTE_ARRAY, offset=0x80, array_size=20,
        default=bytes(bytearray(20)),
        doc="The status map set during SCAMP boot")
    physical_to_virtual_core_map = _Definition(
        _DataType.BYTE_ARRAY, offset=0x94, array_size=20,
        default=bytes(bytearray(20)),
        doc="The physical core ID to virtual core ID map")
    virtual_to_physical_core_map = _Definition(
        _DataType.BYTE_ARRAY, offset=0xa8, array_size=20,
        default=bytes(bytearray(20)),
        doc="The virtual core ID to physical core ID map")
    n_working_cores = _Definition(
        _DataType.BYTE, offset=0xbc,
        doc="The number of working cores")
    n_scamp_working_cores = _Definition(
        _DataType.BYTE, offset=0xbd,
        doc="The number of SCAMP working cores")
    padding_3 = _Definition(
        _DataType.SHORT, offset=0xbe,
        doc="A short of padding")
    sdram_base_address = _Definition(
        _DataType.INT, offset=0xc0,
        doc="The base address of SDRAM")
    system_ram_base_address = _Definition(
        _DataType.INT, offset=0xc4,
        doc="The base address of System RAM")
    system_sdram_base_address = _Definition(
        _DataType.INT, offset=0xc8,
        doc="The base address of System SDRAM")
    cpu_information_base_address = _Definition(
        _DataType.INT, offset=0xcc,
        doc="The base address of the CPU information blocks")
    system_sdram_heap_address = _Definition(
        _DataType.INT, offset=0xd0,
        doc="The base address of the system SDRAM heap")
    router_table_copy_address = _Definition(
        _DataType.INT, offset=0xd4,
        doc="The address of the copy of the routing tables")
    peer_to_peer_hop_table_address = _Definition(
        _DataType.INT, offset=0xd8,
        doc="The address of the peer-to-peer hop tables")
    allocated_tag_table_address = _Definition(
        _DataType.INT, offset=0xdc,
        doc="The address of the allocated tag table")
    first_free_router_entry = _Definition(
        _DataType.SHORT, offset=0xe0,
        doc="The ID of the first free router entry")
    n_active_peer_to_peer_addresses = _Definition(
        _DataType.SHORT, offset=0xe2,
        doc="The number of active peer-to-peer addresses")
    app_data_table_address = _Definition(
        _DataType.INT, offset=0xe4,
        doc="The address of the application data table")
    shared_message_buffer_address = _Definition(
        _DataType.INT, offset=0xe8,
        doc="The address of the shared message buffers")
    monitor_mailbox_flags = _Definition(
        _DataType.INT, offset=0xec,
        doc="The monitor incoming mailbox flags")
    ethernet_ip_address = _Definition(
        _DataType.BYTE_ARRAY, offset=0xf0, array_size=4,
        default=bytes(bytearray(4)),
        doc="The IP address of the chip")
    fixed_route_copy = _Definition(
        _DataType.INT, offset=0xf4,
        doc="A (virtual) copy of the router FR register")
    board_info = _Definition(
        _DataType.INT, offset=0xf8,
        doc="A pointer to the board information structure")
    padding_4 = _Definition(
        _DataType.INT, offset=0xfc,
        doc="A word of padding")

    def __init__(self, offset, data_type, default, array_size, doc):
        """
        :param _DataType data_type: The data type of the variable
        :param int offset: The offset from the start of the system variable
            structure where the variable is found
        :param object default:
            The default value assigned to the variable if not overridden
        :param array_size: The length of the array, or `None` if not an array
        :type array_size: int or None
        """
        # pylint: disable=too-many-arguments
        self._data_type = data_type
        self._offset = offset
        self._default = default
        self._array_size = array_size
        self.__doc__ = doc

    @property
    def data_type(self):
        return self._data_type

    @property
    def array_size(self):
        return self._array_size

    @property
    def offset(self):
        return self._offset

    @property
    def default(self):
        return self._default


class SystemVariableBootValues(object):
    """
    Default values of the system variables that get passed to SpiNNaker
    during boot.
    """
    __slot__ = [
        "_values"]

    def __init__(self, hardware_version=None, led_0=None):
        # Create a dict of variable values
        self._values = dict()
        for variable in SystemVariableDefinition:
            self._values[variable] = variable.default

        if hardware_version is not None:
            self._values[SystemVariableDefinition.hardware_version] =\
                hardware_version
        if led_0 is not None:
            self._values[SystemVariableDefinition.led_0] = led_0

    def set_value(self, system_variable_definition, value):
        self._values[system_variable_definition] = value

    @property
    def bytestring(self):
        data = b""
        for sys_var in SystemVariableDefinition:
            data += struct.pack(sys_var.data_type.struct_code,
                                self._values[sys_var])
        return data


spinnaker_boot_values = {
    1: SystemVariableBootValues(
        hardware_version=1, led_0=0x00076104),
    2: SystemVariableBootValues(
        hardware_version=2, led_0=0x00006103),
    3: SystemVariableBootValues(
        hardware_version=3, led_0=0x00000502),
    4: SystemVariableBootValues(
        hardware_version=4, led_0=0x00000001),
    5: SystemVariableBootValues(
        hardware_version=5, led_0=0x00000001)}
