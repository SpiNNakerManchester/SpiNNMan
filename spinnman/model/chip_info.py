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

import struct
from typing import Iterable, List, Optional
from spinnman.messages.spinnaker_boot import SystemVariableDefinition


class ChipInfo(object):
    """
    Represents the system variables for a chip, received from the chip SDRAM.
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

    def __init__(self, system_data: bytes, offset: int):
        """
        :param system_data:
            A byte-string retrieved from SDRAM on the board
        :param offset:
            The offset into the byte-string where the actual data starts
        :raise SpinnmanInvalidParameterException:
            If the data doesn't contain valid system data information
        """
        self._system_data = system_data
        self._offset = offset

        links_available = self._read_int("links_available")
        self._links_available: List[int] = list()
        for i in range(6):
            if ((links_available >> i) & 0x1) != 0:
                self._links_available.append(i)

        self._led_flash_period_ms = self._read_int(
            "led_half_period_10_ms") * 10
        self._leds = [self._read_int("led_0"), self._read_int("led_1")]
        self._status_map = self._read_bytes("status_map")
        self._physical_to_virtual_core_map = self._read_bytes(
            "physical_to_virtual_core_map")
        self._virtual_to_physical_core_map = self._read_bytes(
            "virtual_to_physical_core_map")

        self._virtual_core_ids: List[int] = list()
        for virtual_core_id in self._physical_to_virtual_core_map:
            if virtual_core_id != 0xFF:
                self._virtual_core_ids.append(virtual_core_id)
        self._virtual_core_ids.sort()

        ip = self._read_bytes("ethernet_ip_address")
        self._ip_address: Optional[str] = f"{ip[0]}.{ip[1]}.{ip[2]}.{ip[3]}"
        if self._ip_address == "0.0.0.0":
            self._ip_address = None

    def _read_int(self, item: str) -> int:
        item_def = SystemVariableDefinition[item]
        code = item_def.data_type.struct_code
        assert item_def.array_size is None
        value, = struct.unpack_from(
            code, self._system_data, self._offset + item_def.offset)
        return value

    def _read_bytes(self, item: str) -> bytes:
        item_def = SystemVariableDefinition[item]
        assert item_def.array_size is not None
        code = f"{item_def.array_size}{item_def.data_type.struct_code}"
        value, = struct.unpack_from(
            code, self._system_data, self._offset + item_def.offset)
        return value

    @property
    def x(self) -> int:
        """
        The X-coordinate of the chip.
        """
        return self._read_int("x")

    @property
    def y(self) -> int:
        """
        The Y-coordinate of the chip.
        """
        return self._read_int("y")

    @property
    def x_size(self) -> int:
        """
        The number of chips in the X-dimension.
        """
        return self._read_int("x_size")

    @property
    def y_size(self) -> int:
        """
        The number of chips in the Y-dimension.
        """
        return self._read_int("y_size")

    @property
    def nearest_ethernet_x(self) -> int:
        """
        The X-coordinate of the nearest chip with Ethernet.
        """
        return self._read_int("nearest_ethernet_x")

    @property
    def nearest_ethernet_y(self) -> int:
        """
        The Y-coordinate of the nearest chip with Ethernet.
        """
        return self._read_int("nearest_ethernet_y")

    @property
    def is_ethernet_available(self) -> bool:
        """
        Whether the Ethernet is running on this chip.
        """
        return self._read_int("is_ethernet_available") == 1

    @property
    def links_available(self) -> Iterable[int]:
        """
        The links that are available on the chip.
        """
        return self._links_available

    @property
    def cpu_clock_mhz(self) -> int:
        """
        The speed of the CPU clock in MHz.
        """
        return self._read_int("cpu_clock_mhz")

    @property
    def physical_to_virtual_core_map(self) -> bytes:
        """
        The physical core ID to virtual core ID map; entries with a value
        of 0xFF are non-operational cores.
        """
        return self._physical_to_virtual_core_map

    @property
    def virtual_to_physical_core_map(self) -> bytes:
        """
        The virtual core ID to physical core ID map; entries with a value
        of 0xFF are non-operational cores.
        """
        return self._virtual_to_physical_core_map

    @property
    def virtual_core_ids(self) -> Iterable[int]:
        """
        A list of available cores by virtual core ID (including the monitor).
        """
        return self._virtual_core_ids

    @property
    def sdram_base_address(self) -> int:
        """
        The base address of the user region of SDRAM on the chip.
        """
        return self._read_int("sdram_base_address")

    @property
    def system_sdram_base_address(self) -> int:
        """
        The base address of the System SDRAM region on the chip.
        """
        return self._read_int("system_sdram_base_address")

    @property
    def cpu_information_base_address(self) -> int:
        """
        The base address of the CPU information structure.
        """
        return self._read_int("cpu_information_base_address")

    @property
    def first_free_router_entry(self) -> int:
        """
        The ID of the first free routing entry on the chip.
        """
        return self._read_int("first_free_router_entry")

    @property
    def ip_address(self) -> Optional[str]:
        """
        The IP address of the chip, or `None` if no Ethernet.
        """
        return self._ip_address

    @property
    def iobuf_size(self) -> int:
        """
        The size of the IOBUF buffers in bytes.
        """
        return self._read_int("iobuf_size")

    def router_table_copy_address(self) -> int:
        """
        :returns: The address of the copy of the router table.
        """
        return self._read_int("router_table_copy_address")

    @property
    def system_ram_heap_address(self) -> int:
        """
        The address of the base of the heap in system RAM.
        """
        return self._read_int("system_ram_heap_address")

    @property
    def sdram_heap_address(self) -> int:
        """
        The address of the base of the heap in SDRAM.
        """
        return self._read_int("sdram_heap_address")
