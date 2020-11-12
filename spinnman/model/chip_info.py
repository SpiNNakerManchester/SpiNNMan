# Copyright (c) 2017-2019 The University of Manchester
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import struct
from spinnman.messages.spinnaker_boot import SystemVariableDefinition


class ChipInfo(object):
    """ Represents the system variables for a chip, received from the chip\
        SDRAM
    """
    __slots__ = [
        "_ip_address",
        "_led_flash_period_ms",
        "_leds",
        "_links_available",
        "_offset",
        "_physical_to_virtual_core_map",
        "_status_map",
        "_system_data",
        "_virtual_core_ids",
        "_virtual_to_physical_core_map"]

    def __init__(self, system_data, offset):
        """
        :param bytes system_data:
            An bytestring retrieved from SDRAM on the board
        :param int offset:
            The offset into the bytestring where the actual data starts
        :raise SpinnmanInvalidParameterException:
            If the data doesn't contain valid system data information
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

        :rtype: iterable(int)
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
        """ The physical core ID to virtual core ID map; entries with a value\
            of 0xFF are non-operational cores

        :rtype: bytearray
        """
        return self._physical_to_virtual_core_map

    @property
    def virtual_core_ids(self):
        """ A list of available cores by virtual core ID (including the\
            monitor)

        :rtype: iterable(int)
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
        """ The base address of the CPU information structure

        :rtype: int
        """
        return self._read_value("cpu_information_base_address")

    @property
    def first_free_router_entry(self):
        """ The ID of the first free routing entry on the chip

        :rtype: int
        """
        return self._read_value("first_free_router_entry")

    @property
    def ip_address(self):
        """ The IP address of the chip, or None if no Ethernet

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
