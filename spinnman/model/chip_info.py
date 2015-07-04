import struct

# The base address of the system variable structure in System ram
_SYSTEM_VARIABLE_BASE_ADDRESS = 0xf5007f00

# The size of the system variable structure in bytes
_SYSTEM_VARIABLE_BYTES = 256


class ChipInfo(object):
    """ Represents the system variables for a chip, received from the chip\
        SDRAM
    """

    def __init__(self, system_data, offset):
        """

        :param system_data: An bytestring retrieved from SDRAM on the board
        :type system_data: bytestring
        :param offset: The offset into the bytestring where the actual data\
                starts
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If\
                    the data doesn't contain valid system data information
        """
        (self._y, self._x, self._y_size, self._x_size, self._debug_y,
         self._debug_x,                                              # 6B  0
         self._is_peer_to_peer_available,                            # ?   6
         self._nnbc_last_id, self._nearest_ethernet_y,
         self._nearest_ethernet_x, self._hardware_version,           # 4B  7
         self._is_ethernet_available,                                # ?   11
         links_available, self._peer_to_peer_sequence_length,
         self._clock_divisor, _router_phase_timer_scale,             # 4B  12
         # skipped                                                   # 16x 16
         self._router_time_phase_timer,                              # I   32
         self._cpu_clock_mhz, self._memory_clock_mhz,                # 2H  36
         self._nnbc_forward, self._nnbc_retry,
         self._link_timeout_us, led_flash_period_100us,              # 4B  40
         self._peer_to_peer_c_timer, led0, led1,
         self._peer_to_peer_b_timer, self._random_seed,              # 5I  44
         self._is_root_chip,                                         # ?   64
         self._n_shared_message_buffers, self._boot_delay,
         self._soft_watchdog,                                        # 3B  65
         self._probe_timer, self._system_ram_heap_address,
         self._sdram_heap_address, self._iobuf_size,
         self._sdram_buffers_address, self._system_buffers_size,
         self._boot_signature, self._nnbc_memory_pointer,            # 8I  68
         # skipped                                                   # 3x  100
         self._board_test_flags,                                     # B   103
         self._next_free_memory_block_pointer,                       # I   104
         self._n_memory_blocks_in_use, self._maximum_blocks_used,    # 2H  108
         # skipped                                                   # 16x 112
         status_map,                                                 # 20s 128
         physical_to_virtual_core_map,                               # 20s 148
         virtual_to_physical_core_map,                               # 20s 168
         self._n_working_cores, self._n_scamp_working_cores,         # 2B  188
         # skipped                                                   # 2x  190
         self._sdram_base_address, self._sysram_base_address,
         self._system_sdram_base_address, self._cpu_information_base_address,
         self._system_heap_address, self._router_table_copy_address,
         self._peer_to_peer_hop_table_address,
         self._alloc_tag_table_address,                              # 8I  192
         self._first_free_router_entry,
         self._n_active_peer_to_peer_addresses,                      # 2H  224
         self._application_data_address, self._shared_message_buffers_address,
         self._mailbox_flags,                                        # 3I  228
         ip0, ip1, ip2, ip3                                          # 4B  240
         ) = struct.unpack_from(
            "< 6B ? 4B ? 4B 16x I 2H 4B 5I ? 3B 8I 3x B I 2H 16x 20s 20s 20s"
            " 2B 2x 8I 2H 3I 4B",
            system_data, offset)

        self._links_available = list()
        for i in range(0, 8):
            if ((links_available >> i) & 0x1) != 0:
                self._links_available.append(i)

        self._led_flash_period_ms = led_flash_period_100us * 10
        self._leds = [led0, led1]
        self._status_map = bytearray(status_map)
        self._physical_to_virtual_core_map = bytearray(
            physical_to_virtual_core_map)
        self._virtual_to_physical_core_map = bytearray(
            virtual_to_physical_core_map)

        self._virtual_core_ids = list()
        for physical_core_id in range(
                0, len(self._physical_to_virtual_core_map)):
            virtual_core_id = self._physical_to_virtual_core_map[
                physical_core_id]
            if virtual_core_id != 0xFF:
                self._virtual_core_ids.append(virtual_core_id)
        self._virtual_core_ids.sort()

        self._ip_address = "{}.{}.{}.{}".format(ip0, ip1, ip2, ip3)
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
        """ The base address of the user region of SDRAM on the chip

        :rtype: int
        """
        return self._sdram_base_address

    @property
    def system_sdram_base_address(self):
        """ The base address of the System SDRAM region on the chip

        :rtype: int
        """
        return self._system_sdram_base_address

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
