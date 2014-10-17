from spinnman._utils import _get_short_from_little_endian_bytearray
from spinnman._utils import _get_int_from_little_endian_bytearray


def _get_int_from_bytearray(array, offset):
    """ Wrapped functionality in case the endianness changes
    """
    return _get_int_from_little_endian_bytearray(array, offset)


def _get_short_from_bytearray(array, offset):
    """ Wrapped functionality in case the endianness changes
    """
    return _get_short_from_little_endian_bytearray(array, offset)


# The base address of the system variable structure in System ram
_SYSTEM_VARIABLE_BASE_ADDRESS = 0xf5007f00

# The size of the system variable structure in bytes
_SYSTEM_VARIABLE_BYTES = 256


class ChipInfo(object):
    """ Represents the system variables for a chip, received from the chip\
        SDRAM
    """

    def __init__(self, system_data):
        """

        :param system_data: An array of bytes retrieved from SDRAM on the baord
        :type system_data: bytearray
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If\
                    the data doesn't contain valid system data information
        """
        self._y = system_data[0]
        self._x = system_data[1]
        self._y_size = system_data[2]
        self._x_size = system_data[3]
        self._debug_y = system_data[4]
        self._debug_x = system_data[5]
        self._is_peer_to_peer_available = system_data[6] != 0
        self._nnbc_last_id = system_data[7]
        self._nearest_ethernet_y = system_data[8]
        self._nearest_ethernet_x = system_data[9]
        self._hardware_version = system_data[10]
        self._is_ethernet_available = system_data[11] != 0

        self._links_available = list()
        for i in range(0, 8):
            if ((system_data[12] >> i) & 0x1) != 0:
                self._links_available.append(i)

        self._peer_to_peer_sequence_length = system_data[13]
        self._clock_divisor = system_data[14]
        self._router_phase_timer_scale = system_data[15]

        self._router_time_phase_timer = _get_int_from_bytearray(
                system_data, 32)
        self._cpu_clock_mhz = _get_short_from_bytearray(system_data, 36)
        self._memory_clock_mhz = _get_short_from_bytearray(system_data, 38)
        self._nnbc_forward = system_data[40]
        self._nnbc_retry = system_data[41]
        self._link_timeout_us = system_data[42]
        self._led_flash_period_ms = system_data[43] * 10

        self._peer_to_peer_c_timer = _get_int_from_bytearray(system_data, 44)
        self._leds = [_get_int_from_bytearray(system_data, 48),
                      _get_int_from_bytearray(system_data, 52)]
        self._peer_to_peer_b_timer = _get_int_from_bytearray(system_data, 56)
        self._random_seed = _get_int_from_bytearray(system_data, 60)

        self._is_root_chip = system_data[64] != 0
        self._n_shared_message_buffers = system_data[65]
        self._boot_delay = system_data[66]
        self._soft_watchdog = system_data[67]

        self._probe_timer = _get_int_from_bytearray(system_data, 68)

        self._system_ram_heap_address = _get_int_from_bytearray(
                system_data, 72)
        self._sdram_heap_address = _get_int_from_bytearray(system_data, 76)

        self._iobuf_size = _get_int_from_bytearray(system_data, 80)
        self._sdram_buffers_address = _get_int_from_bytearray(system_data, 84)
        self._system_buffers_size = _get_int_from_bytearray(system_data, 88)
        self._boot_signature = _get_int_from_bytearray(system_data, 92)

        self._nnbc_memory_pointer = _get_int_from_bytearray(system_data, 96)

        self._board_test_flags = system_data[103]

        self._next_free_memory_block_pointer = _get_int_from_bytearray(
                system_data, 104)
        self._n_memory_blocks_in_use = _get_short_from_bytearray(
                system_data, 108)
        self._maximum_blocks_used = _get_short_from_bytearray(system_data, 110)

        self._status_map = system_data[128:148]
        self._physical_to_virtual_core_map = system_data[148:168]
        self._virtual_to_physical_core_map = system_data[168:188]

        self._virtual_core_ids = list()
        for physical_core_id in range(0,
                len(self._physical_to_virtual_core_map)):
            virtual_core_id = self._physical_to_virtual_core_map[
                    physical_core_id]
            if virtual_core_id != 0xFF:
                self._virtual_core_ids.append(virtual_core_id)
        self._virtual_core_ids.sort()

        self._n_working_cores = system_data[188]
        self._n_scamp_working_cores = system_data[189]

        self._sdram_base_address = _get_int_from_bytearray(system_data, 192)
        self._sysram_base_address = _get_int_from_bytearray(system_data, 196)
        self._system_sdram_base_address = _get_int_from_bytearray(
                system_data, 200)
        self._cpu_information_base_address = _get_int_from_bytearray(
                system_data, 204)
        self._system_heap_address = _get_int_from_bytearray(system_data, 208)
        self._router_table_copy_address = _get_int_from_bytearray(
                system_data, 212)
        self._peer_to_peer_hop_table_address = _get_int_from_bytearray(
                system_data, 216)
        self._alloc_tag_table_address = _get_int_from_bytearray(
                system_data, 220)

        self._first_free_router_entry = _get_short_from_bytearray(
                system_data, 224)
        self._n_active_peer_to_peer_addresses = _get_short_from_bytearray(
                system_data, 226)
        self._application_data_address = _get_int_from_bytearray(
                system_data, 228)
        self._shared_message_buffers_address = _get_int_from_bytearray(
                system_data, 232)
        self._mailbox_flags = _get_int_from_bytearray(system_data, 236)

        self._ip_address = None
        self._ip_address = "{}.{}.{}.{}".format(
            system_data[240], system_data[241], system_data[242],
            system_data[243])
        if self._ip_address == "0.0.0.0":
            self._ip_address = None

    @property
    def x(self):
        """ The x-coordinate of the chip

        :rtype: int
        """
        return self._x

    @property
    def y(self):
        """ The y-coordinate of the chip

        :rtype: int
        """
        return self._y

    @property
    def x_size(self):
        """ The number of chips in the x-dimension

        :rtype: int
        """
        return self._x_size

    @property
    def y_size(self):
        """ The number of chips in the y-dimension

        :rtype: int
        """
        return self._y_size

    @property
    def nearest_ethernet_x(self):
        """ The x-coordinate of the nearest chip with ethernet

        :rtype: int
        """
        return self._nearest_ethernet_x

    @property
    def nearest_ethernet_y(self):
        """ The y-coordinate of the nearest chip with ethernet

        :rtype: int
        """
        return self._nearest_ethernet_y

    @property
    def is_ethernet_available(self):
        """ True if the ethernet is running on this chip, False otherwise

        :rtype: bool
        """
        return self._is_ethernet_available

    @property
    def links_available(self):
        """ The links that are available on the chip

        :rtype: iterable of int
        """
        return self._links_available

    @property
    def cpu_clock_mhz(self):
        """ The speed of the CPU clock in MHz

        :rtype: int
        """
        return self._cpu_clock_mhz

    @property
    def physical_to_virtual_core_map(self):
        """ The physical core id to virtual core id map; entries with a value\
            of 0xFF are non-operational cores

        :rtype: bytearray
        """
        return self._physical_to_virtual_core_map

    @property
    def virtual_core_ids(self):
        """ A list of available cores by virtual core id (including the\
            monitor)

        :rtype: iterable of int
        """
        return self._virtual_core_ids

    @property
    def sdram_base_address(self):
        """ The base address of SDRAM on the chip

        :rtype: int
        """
        return self._sdram_base_address

    @property
    def cpu_information_base_address(self):
        """ The base address of the cpu information structure

        :rtype: int
        """
        return self._cpu_information_base_address

    @property
    def first_free_router_entry(self):
        """ The id of the first free routing entry on the chip

        :rtype: int
        """
        return self._first_free_router_entry

    @property
    def ip_address(self):
        """ The ip address of the chip, or None if no ethernet

        :rtype: str
        """
        return self._ip_address

    @property
    def iobuf_size(self):
        """ The size of the iobuf buffers in bytes

        :rtype: int
        """
        return self._iobuf_size

    def router_table_copy_address(self):
        """ The address of the copy of the router table

        :rtype: int
        """
        return self._router_table_copy_address
