from spinnman.messages.spinnaker_boot import SystemVariableDefinition

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
        :type system_data: str
        :param offset: The offset into the bytestring where the actual data\
                starts
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If\
                    the data doesn't contain valid system data information
        """
        self._system_data = system_data
        self._offset = offset

        links_available = self._read_value("links_available")
        self._links_available = list()
        for i in range(0, 6):
            if ((links_available >> i) & 0x1) != 0:
                self._links_available.append(i)

        self._led_flash_period_ms = self._read_value(
            "led_half_period_10_ms") * 10
        self._leds = [self._read_value("led_0"), self._read_value("led_1")]
        self._status_map = bytearray(self._read_value("status_map"))
        self._physical_to_virtual_core_map = bytearray(
            self._read_value("physical_to_virtual_core_map"))
        self._virtual_to_physical_core_map = bytearray(
            self._read_value("virtual_to_physical_core_map"))

        self._virtual_core_ids = list()
        for physical_core_id in range(
                0, len(self._physical_to_virtual_core_map)):
            virtual_core_id = self._physical_to_virtual_core_map[
                physical_core_id]
            if virtual_core_id != 0xFF:
                self._virtual_core_ids.append(virtual_core_id)
        self._virtual_core_ids.sort()

        ip = bytearray(self._read_value("ethernet_ip_address"))
        self._ip_address = "{}.{}.{}.{}".format(ip[0], ip[1], ip[2], ip[3])
        if self._ip_address == "0.0.0.0":
            self._ip_address = None

    def _read_value(self, item):
        item_def = SystemVariableDefinition[item]
        code = item_def.data_type.struct_code
        if item_def.array_size is not None:
            code = "{}{}".format(item_def.array_size, code)
        values = struct.unpack_from(
            code, self._system_data, self._offset + item_def.offset)
        return values[0]

    def __getattr__(self, item):
        return self._read_value(item)

    @property
    def x(self):
        """ The x-coordinate of the chip

        :rtype: int
        """
        return self._read_value("x")

    @property
    def y(self):
        """ The y-coordinate of the chip

        :rtype: int
        """
        return self._read_value("y")

    @property
    def x_size(self):
        """ The number of chips in the x-dimension

        :rtype: int
        """
        return self._read_value("x_size")

    @property
    def y_size(self):
        """ The number of chips in the y-dimension

        :rtype: int
        """
        return self._read_value("y_size")

    @property
    def nearest_ethernet_x(self):
        """ The x-coordinate of the nearest chip with Ethernet

        :rtype: int
        """
        return self._read_value("nearest_ethernet_x")

    @property
    def nearest_ethernet_y(self):
        """ The y-coordinate of the nearest chip with Ethernet

        :rtype: int
        """
        return self._read_value("nearest_ethernet_y")

    @property
    def is_ethernet_available(self):
        """ True if the Ethernet is running on this chip, False otherwise

        :rtype: bool
        """
        return self._read_value("is_ethernet_available") == 1

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
        return self._read_value("cpu_clock_mhz")

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
        return self._read_value("sdram_base_address")

    @property
    def system_sdram_base_address(self):
        """ The base address of the System SDRAM region on the chip

        :rtype: int
        """
        return self._read_value("system_sdram_base_address")

    @property
    def cpu_information_base_address(self):
        """ The base address of the cpu information structure

        :rtype: int
        """
        return self._read_value("cpu_information_base_address")

    @property
    def first_free_router_entry(self):
        """ The id of the first free routing entry on the chip

        :rtype: int
        """
        return self._read_value("first_free_router_entry")

    @property
    def ip_address(self):
        """ The ip address of the chip, or None if no Ethernet

        :rtype: str
        """
        return self._ip_address

    @property
    def iobuf_size(self):
        """ The size of the iobuf buffers in bytes

        :rtype: int
        """
        return self._read_value("iobuf_size")

    def router_table_copy_address(self):
        """ The address of the copy of the router table

        :rtype: int
        """
        return self._read_value("router_table_copy_address")

    @property
    def system_ram_heap_address(self):
        """ The address of the base of the heap in system RAM

        :rtype: int
        """
        return self._read_value("system_ram_heap_address")

    @property
    def sdram_heap_address(self):
        """ The address of the base of the heap in SDRAM

        :rtype: int
        """
        return self._read_value("sdram_heap_address")
