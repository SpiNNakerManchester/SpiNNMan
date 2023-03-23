# Copyright (c) 2016 The University of Manchester
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
from spinnman.model.enums import CPUState
from spinn_machine.machine import Machine

_THREE_WORDS = struct.Struct("<3I")
_TWO_BYTES = struct.Struct("<BB")
_FOUR_BYTES = struct.Struct("<4B")
_EIGHTEEN_BYTES = struct.Struct("<18B")
_ONE_SHORT = struct.Struct("<H")


class ChipSummaryInfo(object):
    """
    Represents the chip summary information read via an SCP command.
    """
    __slots__ = [
        "_core_states",
        "_ethernet_ip_address",
        "_is_ethernet_available",
        "_largest_free_sdram_block",
        "_largest_free_sram_block",
        "_n_cores",
        "_n_free_multicast_routing_entries",
        "_nearest_ethernet_x",
        "_nearest_ethernet_y",
        "_parent_link",
        "_working_links",
        "_x", "_y"]

    def __init__(self, chip_summary_data, offset, x, y):
        """
        :param bytes chip_summary_data: The data from the SCP response
        :param int offset: The offset into the data where the data starts
        :param int x: The x-coordinate of the chip that this data is from
        :param int y: The y-coordinate of the chip that this data is from
        """
        (chip_summary_flags, self._largest_free_sdram_block,
            self._largest_free_sram_block) = _THREE_WORDS.unpack_from(
                chip_summary_data, offset)
        self._n_cores = chip_summary_flags & 0x1F
        self._working_links = [
            link for link in range(0, 6)
            if chip_summary_flags >> (8 + link) & 1 != 0]
        self._n_free_multicast_routing_entries = \
            (chip_summary_flags >> 14) & 0x7FF
        self._is_ethernet_available = bool(chip_summary_flags & (1 << 25))

        data_offset = offset + 12
        self._core_states = [
            CPUState(state) for state in
            _EIGHTEEN_BYTES.unpack_from(chip_summary_data, data_offset)]
        data_offset += 18

        self._x = x
        self._y = y

        self._nearest_ethernet_x = None
        self._nearest_ethernet_y = None
        self._ethernet_ip_address = None

        (self._nearest_ethernet_y, self._nearest_ethernet_x) = \
            _TWO_BYTES.unpack_from(chip_summary_data, data_offset)
        data_offset += 2

        ip = _FOUR_BYTES.unpack_from(chip_summary_data, data_offset)
        ethernet_ip_address = f"{ip[0]}.{ip[1]}.{ip[2]}.{ip[3]}"
        if ethernet_ip_address != "0.0.0.0":
            self._ethernet_ip_address = ethernet_ip_address
        data_offset += 4

        # In case the data hasn't been added in the version of SCAMP being used
        self._parent_link = None
        if len(chip_summary_data) > data_offset:
            (self._parent_link, ) = _ONE_SHORT.unpack_from(
                chip_summary_data, data_offset)
            # The root chip will use the P2P "self", which is outside the range
            # of valid links, so check and skip this one
            if self._parent_link > len(Machine.LINK_ADD_TABLE):
                self._parent_link = None
            data_offset += 2

    @property
    def x(self):
        """
        The X-coordinate of the chip that this data is from.

        :rtype: int
        """
        return self._x

    @property
    def y(self):
        """
        The Y-coordinate of the chip that this data is from.

        :rtype: int
        """
        return self._y

    @property
    def n_cores(self):
        """
        The number of cores working on the chip (including monitors).

        :rtype: int
        """
        return self._n_cores

    @property
    def core_states(self):
        """
        The state of the cores on the chip (list of one per core).

        :rtype: list(CPUState)
        """
        return self._core_states

    @property
    def working_links(self):
        """
        The IDs of the working links outgoing from this chip.

        :rtype: list(int)
        """
        return self._working_links

    @property
    def is_ethernet_available(self):
        """
        Whether the Ethernet connection is available on this chip.

        :rtype: bool
        """
        return self._is_ethernet_available

    @property
    def n_free_multicast_routing_entries(self):
        """
        The number of multicast routing entries free on this chip.

        :rtype: int
        """
        return self._n_free_multicast_routing_entries

    @property
    def largest_free_sdram_block(self):
        """
        The size of the largest block of free SDRAM in bytes.

        :rtype: int
        """
        return self._largest_free_sdram_block

    @property
    def largest_free_sram_block(self):
        """
        The size of the largest block of free SRAM in bytes.

        :rtype: int
        """
        return self._largest_free_sram_block

    @property
    def nearest_ethernet_x(self):
        """
        The X-coordinate of the nearest Ethernet chip.

        :rtype: int
        """
        return self._nearest_ethernet_x

    @property
    def nearest_ethernet_y(self):
        """
        The Y-coordinate of the nearest Ethernet chip.

        :rtype: int
        """
        return self._nearest_ethernet_y

    @property
    def ethernet_ip_address(self):
        """
        The IP address of the Ethernet if up, or `None` if not.

        :rtype: str
        """
        return self._ethernet_ip_address

    def clear_ethernet_ip_address(self):
        """
        Forces the Ethernet IP address to `None`, in case of an errant chip.
        """
        self._ethernet_ip_address = None

    @property
    def parent_link(self):
        """
        The link to the parent of the chip in the tree of chips from root.

        :rtype: int
        """
        return self._parent_link

    def __repr__(self):
        return f"x:{self.x} y:{self.y} n_cores:{self.n_cores}"
