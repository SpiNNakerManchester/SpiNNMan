from enum import Enum
from collections import namedtuple

_SYSTEM_VARIABLES_BOOT_SIZE = 128


class _DataType(Enum):
    """ Enum for data types
    """
    BYTE = 1
    SHORT = 2
    INT = 4
    LONG = 8


class _Definition(namedtuple("_Definition",
        "offset, data_type, default, array_size, doc")):

    def __new__(cls, data_type, offset, default=0, array_size=None, doc=""):
        return super(_Definition, cls).__new__(cls, offset, data_type, default,
                array_size, doc)


class _SystemVariableDefinition(Enum):
    """ Defines the system variables available
    """

    x = _Definition(_DataType.BYTE, offset=0,
            doc="The x-coordinate of the chip")
    y = _Definition(_DataType.BYTE, offset=0x01,
            doc="The y-coordinate of the chip")
    x_size = _Definition(_DataType.BYTE, offset=0x02,
            doc="The number of chips in the x-dimension")
    y_size = _Definition(_DataType.BYTE, offset=0x03,
            doc="The number of chips in the y-dimension")
    debug_x = _Definition(_DataType.BYTE, offset=0x04,
            doc="The x-coordinate of the chip to send debug messages to")
    debug_y = _Definition(_DataType.BYTE, offset=0x05,
            doc="The y-coordinate of the chip to send debug messages to")
    is_peer_to_peer_available = _Definition(_DataType.BYTE, offset=0x06,
            doc="Indicates if peer-to-peer is working on the chip")
    nearest_neighbour_last_id = _Definition(_DataType.BYTE, offset=0x07,
            doc="The last id used in nearest neighbor transaction")
    nearest_ethernet_x = _Definition(_DataType.BYTE, offset=0x08,
            doc="The x-coordinate of the nearest chip with ethernet")
    nearest_ethernet_y = _Definition(_DataType.BYTE, offset=0x09,
            doc="The y-coordinate of the nearest chip with ethernet")
    hardware_version = _Definition(_DataType.BYTE, offset=0x0a,
            doc="The version of the hardware in use")
    is_ethernet_available = _Definition(_DataType.BYTE, offset=0x0b,
            doc="Indicates if ethernet is available on this chip")
    links_available = _Definition(_DataType.BYTE, offset=0x0c,
            doc="A bit-mask indicating which links are available")
    log_peer_to_peer_sequence_length = _Definition(_DataType.BYTE, offset=0x0d,
            default=4,
            doc="Log (base 2) of the peer-to-peer sequence length")
    clock_divisor = _Definition(_DataType.BYTE, offset=0x0e,
            default=0x33,
            doc="The clock divisors for system & router clocks")
    time_phase_scale = _Definition(_DataType.BYTE, offset=0x0f,
            doc="The time-phase scaling factor")
    clock_milliseconds = _Definition(_DataType.LONG, offset=0x10,
            doc="The time since startup in milliseconds")
    time_milliseconds = _Definition(_DataType.SHORT, offset=0x18,
            doc="The number of milliseconds in the current second")
    ltpc_period = _Definition(_DataType.SHORT, offset=0x1a)
    unix_timestamp = _Definition(_DataType.INT, offset=0x1c,
            doc="The time in seconds since midnight, 1st January 1970")
    router_time_phase_timer = _Definition(_DataType.INT, offset=0x20,
            doc="The router time-phase timer")
    cpu_clock_frequency_mhz = _Definition(_DataType.SHORT, offset=0x24,
            default=150,
            doc="The CPU clock frequency in MHz")
    sdram_clock_frequency_mhz = _Definition(_DataType.SHORT, offset=0x26,
            default=130,
            doc="The SDRAM clock frequency in MHz")
    nearest_neighbour_forward = _Definition(_DataType.BYTE, offset=0x28,
            default=0x3F,
            doc="Nearest-Neighbor forward parameter")
    nearest_neighbour_retry = _Definition(_DataType.BYTE, offset=0x29,
            doc="Nearest-Neighbor retry parameter")
    link_peek_timeout_microseconds = _Definition(_DataType.BYTE, offset=0x2a,
            default=100,
            doc="The link peek/poke timeout in microseconds")
    led_half_period_10_ms = _Definition(_DataType.BYTE, offset=0x2b,
            default=50,
            doc="The LED half-period in 10 ms units")
    peer_to_peer_c_pkt_timer = _Definition(_DataType.INT, offset=0x2c,
            default=0x02020a52,
            doc="The peer-to-peer C packet timer")
    led_0 = _Definition(_DataType.INT, offset=0x30,
            default=0x1,
            doc="The first part of the LED definitions")
    led_1 = _Definition(_DataType.INT, offset=0x34,
            doc="The last part of the LED definitions")
    peer_to_peer_b_pkt_timer = _Definition(_DataType.INT, offset=0x38,
            default=0x01320001,
            doc="The peer-to-peer B packet timer")
    random_seed = _Definition(_DataType.INT, offset=0x3c,
            doc="The random seed")
    is_root_chip = _Definition(_DataType.BYTE, offset=0x40,
            doc="Indicates if this is the root chip")
    n_shared_message_buffers = _Definition(_DataType.BYTE, offset=0x41,
            default=7,
            doc="The number of shared message buffers")
    nearest_neighbour_delay_us = _Definition(_DataType.BYTE, offset=0x42,
            default=10,
            doc="The delay between nearest-neighbor packets in microseconds")
    software_watchdog_count = _Definition(_DataType.BYTE, offset=0x43,
            default=3,
            doc="The number of watchdog timeouts before an error is raised")
    probe_timer = _Definition(_DataType.INT, offset=0x44,
            default=0x010a0001,
            doc="The probe timer")
    user_system_ram_heap_words = _Definition(_DataType.INT, offset=0x48,
            default=1024,
            doc="The size of the user system RAM heap in bytes")
    user_sdram_heap_words = _Definition(_DataType.INT, offset=0x4c,
            default=1048576,
            doc="The size of the user SDRAM heap in bytes")
    iobuf_bytes = _Definition(_DataType.INT, offset=0x50,
            default=16384,
            doc="The size of the iobuf buffer in bytes")
    system_sdram_bytes = _Definition(_DataType.INT, offset=0x54,
            default=8388608,
            doc="The size of the system SDRAM in bytes")
    system_buffer_words = _Definition(_DataType.INT, offset=0x58,
            default=32768,
            doc="The size of the system buffer in words")
    boot_signature = _Definition(_DataType.INT, offset=0x5c,
            doc="The boot signature")
    nearest_neighbour_memory_pointer = _Definition(_DataType.INT, offset=0x60,
            doc="The memory pointer for nearest neighbor global operations")
    lock_0 = _Definition(_DataType.BYTE, offset=0x64,
            doc="The first lock")
    lock_1 = _Definition(_DataType.BYTE, offset=0x65,
            doc="The second lock")
    lock_2 = _Definition(_DataType.BYTE, offset=0x66,
            doc="The third lock")
    board_test_flags = _Definition(_DataType.BYTE, offset=0x67,
            doc="Board testing flags")
    shared_message_first_free_address = _Definition(_DataType.INT, offset=0x68,
            doc="Pointer to the first free shared message buffer")
    shared_message_count_in_use = _Definition(_DataType.SHORT, offset=0x6c,
            doc="The number of shared message buffers in use")
    shared_message_maximum_used = _Definition(_DataType.SHORT, offset=0x6e,
            doc="The maximum number of shared message buffers used")
    padding_1 = _Definition(_DataType.INT, offset=0x70,
            doc="The first padding word")
    padding_2 = _Definition(_DataType.INT, offset=0x74,
            doc="The second padding word")
    padding_3 = _Definition(_DataType.INT, offset=0x78,
            doc="The third padding word")
    padding_4 = _Definition(_DataType.INT, offset=0x7c,
            doc="The fourth padding word")
    status_map = _Definition(_DataType.BYTE, offset=0x80,
            array_size=20,
            doc="The status map set during SCAMP boot")
    physical_to_virtual_core_map = _Definition(_DataType.BYTE, offset=0x94,
            array_size=20,
            doc="The physical core id to virtual core id map")
    virtual_to_physical_core_map = _Definition(_DataType.BYTE, offset=0xa8,
            array_size=20,
            doc="The virtual core id to physical core id map")
    n_working_cores = _Definition(_DataType.BYTE, offset=0xbc,
            doc="The number of working cores")
    n_scamp_working_cores = _Definition(_DataType.BYTE, offset=0xbd,
            doc="The number of SCAMP working cores")
    padding_5 = _Definition(_DataType.SHORT, offset=0xbe,
            doc="The fifth padding short")
    sdram_base_address = _Definition(_DataType.INT, offset=0xc0,
            doc="The base address of SDRAM")
    system_ram_base_address = _Definition(_DataType.INT, offset=0xc4,
            doc="The base address of System RAM")
    system_sdram_base_address = _Definition(_DataType.INT, offset=0xc8,
            doc="The base address of System SDRAM")
    cpu_information_base_address = _Definition(_DataType.INT, offset=0xcc,
            doc="The base address of the cpu information blocks")
    system_heap_sdram_base_address = _Definition(_DataType.INT, offset=0xd0,
            doc="The base address of the system SDRAM heap")
    routing_table_copy_address = _Definition(_DataType.INT, offset=0xd4,
            doc="The address of the copy of the routing tables")
    peer_to_peer_hop_table_address = _Definition(_DataType.INT, offset=0xd8,
            doc="The address of the peer-to-peer hop tables")
    allocated_tag_table_address = _Definition(_DataType.INT, offset=0xdc,
            doc="The address of the allocated tag table")
    router_first_free_entry = _Definition(_DataType.SHORT, offset=0xe0,
            doc="The id of the first free router entry")
    n_active_peer_to_peer_addresses = _Definition(_DataType.SHORT, offset=0xe2,
            doc="The number of active peer-to-peer addresses")
    app_data_table_address = _Definition(_DataType.INT, offset=0xe4,
            doc="The address of the application data table")
    shared_message_buffer_address = _Definition(_DataType.INT, offset=0xe8,
            doc="The address of the shared message buffers")
    monitor_mailbox_flags = _Definition(_DataType.INT, offset=0xec,
            doc="The monitor incoming mailbox flags")
    ethernet_ip_address = _Definition(_DataType.BYTE, offset=0xf0,
            array_size=4,
            doc="The ip address of the chip")
    user_temp_1 = _Definition(_DataType.INT, offset=0xf4,
            doc="The first user variable")
    user_temp_2 = _Definition(_DataType.INT, offset=0xf8,
            doc="The second user variable")
    user_temp_3 = _Definition(_DataType.INT, offset=0xfc,
            doc="The third user variable")

    def __init__(self, offset, data_type, default, array_size, doc):
        """

        :param data_type: The data type of the variable
        :type data_type: :py:class:`_DataType`
        :param offset: The offset from the start of the system variable\
                    structure where the variable is found
        :type offset: int
        :param default: The default value assigned to the variable\
                    if not overridden
        :type default: int
        :param array_size: The length of the array, or None if not an array
        :type array_size: int
        """
        self._data_type = data_type
        self._offset = offset
        self._default = default
        self._array_size = array_size
        self.__doc__ = doc

    @property
    def data_type(self):
        return self._data_type

    @property
    def offset(self):
        return self._offset

    @property
    def default(self):
        return self._default


class SystemVariableBootValues(object):
    """ Default values of the system variables that get passed to SpiNNaker\
        during boot
    """

    def __init__(self, x_size, y_size, hardware_version,
            cpu_clock_frequency_mhz, led_0):

        # Create a dict of variable values
        self._values = dict()
        for variable in _SystemVariableDefinition:
            self._values[variable] = variable.default

        self._values[_SystemVariableDefinition.x_size] = x_size
        self._values[_SystemVariableDefinition.y_size] = y_size
        self._values[_SystemVariableDefinition.hardware_version] =\
                hardware_version
        self._values[_SystemVariableDefinition.cpu_clock_frequency_mhz] =\
                cpu_clock_frequency_mhz
        self._values[_SystemVariableDefinition.led_0] = led_0

    def set_value(self, system_variable_definition, value):
        self._values[system_variable_definition] = value

    def write_values(self, byte_writer):
        for sys_var in _SystemVariableDefinition:
            if sys_var.data_type == _DataType.BYTE:
                byte_writer.write_byte(self._values[sys_var])
            elif sys_var.data_type == _DataType.SHORT:
                byte_writer.write_short(self._values[sys_var])
            elif sys_var.data_type == _DataType.INT:
                byte_writer.write_int(self._values[sys_var])
            elif sys_var.data_type == _DataType.LONG:
                byte_writer.write_long(self._values[sys_var])

spinnaker_boot_values = {
        1: SystemVariableBootValues(x_size=2, y_size=2, hardware_version=1,
                cpu_clock_frequency_mhz=200, led_0=0x00076104),
        2: SystemVariableBootValues(x_size=2, y_size=2, hardware_version=2,
                cpu_clock_frequency_mhz=200, led_0=0x00006103),
        3: SystemVariableBootValues(x_size=2, y_size=2, hardware_version=3,
                cpu_clock_frequency_mhz=200, led_0=0x00000502),
        4: SystemVariableBootValues(x_size=8, y_size=8, hardware_version=4,
                cpu_clock_frequency_mhz=200, led_0=0x00000001),
        5: SystemVariableBootValues(x_size=8, y_size=8, hardware_version=5,
                cpu_clock_frequency_mhz=200, led_0=0x00000001),
        }
""" Configuration for different board types
"""
