# Copyright (c) 2015 The University of Manchester
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

from collections import defaultdict
from contextlib import suppress
import logging
import functools
from os.path import join
from spinn_utilities.config_holder import (
    get_config_bool, get_config_int, get_config_str)
from spinn_utilities.data import UtilsDataView
from spinn_utilities.log import FormatAdapter
from spinn_machine import (
    Router, Chip, SDRAM, Link, machine_from_size)
from spinn_machine.ignores import IgnoreChip, IgnoreCore, IgnoreLink
from spinn_machine import Machine
from spinn_machine.machine_factory import machine_repair
from spinnman.constants import (
    ROUTER_REGISTER_P2P_ADDRESS, SYSTEM_VARIABLE_BASE_ADDRESS)
from spinnman.messages.spinnaker_boot import (
    SystemVariableDefinition)
from spinnman.exceptions import SpinnmanUnexpectedResponseCodeException
from spinnman.messages.scp.impl import ReadMemory, ReadLink, GetChipInfo
from spinnman.model import P2PTable
from spinnman.model.enums import CPUState
from .abstract_multi_connection_process import AbstractMultiConnectionProcess

logger = FormatAdapter(logging.getLogger(__name__))

REPORT_FILE = "Ignores_report.rpt"

P_TO_V = SystemVariableDefinition.physical_to_virtual_core_map
V_TO_P = SystemVariableDefinition.virtual_to_physical_core_map
P_TO_V_ADDR = SYSTEM_VARIABLE_BASE_ADDRESS + P_TO_V.offset
P_MAPS_SIZE = P_TO_V.array_size + V_TO_P.array_size


class GetMachineProcess(AbstractMultiConnectionProcess):
    """
    A process for getting the machine details over a set of connections.
    """
    __slots__ = [
        "_chip_info",
        # Used if there are any ignores with ip addresses
        # Holds a mapping from ip to board root (x,y)
        "_ethernets",
        # Holds a map from x,y to a set of virtual cores to ignores
        "_ignore_cores_map",
        "_p2p_column_data",
        # Holds a mapping from (x,y) to a mapping of physical to virtual core
        "_virtual_to_physical_map",
        # Holds a mapping from (x,y) to a mapping of virtual to physical core
        "_physical_to_virtual_map"]

    def __init__(self, connection_selector):
        """
        :param connection_selector:
        :type connection_selector:
            AbstractMultiConnectionProcessConnectionSelector
        """
        super().__init__(connection_selector)

        self._ignore_cores_map = defaultdict(set)

        self._p2p_column_data = list()

        # A dictionary of (x, y) -> ChipInfo
        self._chip_info = dict()

        # Set ethernets to None meaning not computed yet
        self._ethernets = None

        # Maps between virtual and physical cores
        self._virtual_to_physical_map = dict()
        self._physical_to_virtual_map = dict()

    def _make_chip(self, chip_info, machine):
        """
        Creates a chip from a ChipSummaryInfo structure.

        :param ChipSummaryInfo chip_info:
            The ChipSummaryInfo structure to create the chip from
        :return: The created chip
        :rtype: ~spinn_machine.Chip
        """
        # Create the down cores set if any
        n_cores = min(chip_info.n_cores, Machine.max_cores_per_chip())
        core_states = chip_info.core_states
        down_cores = self._ignore_cores_map.get(
            (chip_info.x, chip_info.y), None)
        for i in range(1, n_cores):
            if core_states[i] != CPUState.IDLE:
                self._report_ignore(
                    "Not using core {}, {}, {} in state {}",
                    chip_info.x, chip_info.y, i,  core_states[i])
                if down_cores is None:
                    down_cores = set()
                down_cores.add(i)

        # Create the router
        router = self._make_router(chip_info, machine)

        # Create the chip's SDRAM object
        sdram_size = chip_info.largest_free_sdram_block
        max_sdram_size = get_config_int(
            "Machine", "max_sdram_allowed_per_chip")
        if (max_sdram_size is not None and
                sdram_size > max_sdram_size):
            sdram_size = max_sdram_size
        sdram = SDRAM(size=sdram_size)

        # Create the chip
        return Chip(
            x=chip_info.x, y=chip_info.y, n_processors=n_cores,
            router=router, sdram=sdram,
            ip_address=chip_info.ethernet_ip_address,
            nearest_ethernet_x=chip_info.nearest_ethernet_x,
            nearest_ethernet_y=chip_info.nearest_ethernet_y,
            down_cores=down_cores, parent_link=chip_info.parent_link,
            v_to_p_map=self._virtual_to_physical_map.get(
                (chip_info.x, chip_info.y)))

    def _make_router(self, chip_info, machine):
        """
        :param ChipSummaryInfo chip_info:
        :param ~spinn_machine.Machine machine:
        :rtype: ~spinn_machine.Router
        """
        links = list()
        for link in chip_info.working_links:
            dest_xy = machine.xy_over_link(chip_info.x, chip_info.y, link)
            if dest_xy in self._chip_info:
                links.append(Link(
                    chip_info.x, chip_info.y, link, dest_xy[0], dest_xy[1]))
            else:
                logger.warning(
                    "Link {},{}:{} points to {} but that is not included ",
                    chip_info.x, chip_info.y, link, dest_xy)

        return Router(
            links=links,
            n_available_multicast_entries=(
                chip_info.n_free_multicast_routing_entries))

    def __receive_p2p_data(self, column, scp_read_response):
        """
        :param int column:
        :param _SCPReadMemoryResponse scp_read_response:
        """
        self._p2p_column_data[column] = (
            scp_read_response.data, scp_read_response.offset)

    def _receive_chip_info(self, scp_read_chip_info_response):
        """
        :param GetChipInfoResponse scp_read_chip_info_response:
        """
        chip_info = scp_read_chip_info_response.chip_info
        self._chip_info[chip_info.x, chip_info.y] = chip_info

    def _receive_p_maps(self, x, y, scp_read_response):
        """
        Receive the physical-to-virtual and virtual-to-physical maps.

        :param _SCPReadMemoryResponse scp_read_response:
        """
        data = scp_read_response.data
        off = scp_read_response.offset
        self._physical_to_virtual_map[x, y] = bytearray(
            data[off:P_TO_V.array_size + off])
        off += P_TO_V.array_size
        self._virtual_to_physical_map[x, y] = bytearray(data[off:])

    def _receive_error(self, request, exception, tb, connection):
        """
        :param AbstractSCPRequest request:
        :param Exception exception:
        """
        # If we get an ReadLink with a
        # SpinnmanUnexpectedResponseCodeException, this is a failed link
        # and so can be ignored
        if isinstance(request, ReadLink):
            if isinstance(exception, SpinnmanUnexpectedResponseCodeException):
                return
        super()._receive_error(request, exception, tb, connection)

    def get_machine_details(self, boot_x, boot_y, width, height):
        """
        :param int boot_x:
        :param int boot_y:
        :param int width:
        :param int height:
        :rtype: ~spinn_machine.Machine
        """
        # Get the P2P table - 8 entries are packed into each 32-bit word
        p2p_column_bytes = P2PTable.get_n_column_bytes(height)
        self._p2p_column_data = [None] * width
        for column in range(width):
            offset = P2PTable.get_column_offset(column)
            self._send_request(
                ReadMemory(
                    x=boot_x, y=boot_y,
                    base_address=(ROUTER_REGISTER_P2P_ADDRESS + offset),
                    size=p2p_column_bytes),
                functools.partial(self.__receive_p2p_data, column))
        self._finish()
        self.check_for_error()
        p2p_table = P2PTable(width, height, self._p2p_column_data)

        # Get the chip information for each chip
        for (x, y) in p2p_table.iterchips():
            self._send_request(GetChipInfo(x, y), self._receive_chip_info)
            self._send_request(
                ReadMemory(x, y, P_TO_V_ADDR, P_MAPS_SIZE),
                functools.partial(self._receive_p_maps, x, y))
        self._finish()
        with suppress(Exception):
            # Ignore errors, as any error here just means that a chip
            # is down that wasn't marked as down
            self.check_for_error()

        # Warn about unexpected missing chips
        for (x, y) in p2p_table.iterchips():
            if (x, y) not in self._chip_info:
                logger.warning(
                    "Chip {}, {} was expected but didn't reply", x, y)

        machine = machine_from_size(width, height)
        self._preprocess_ignore_chips(machine)
        self._process_ignore_links(machine)
        self._preprocess_ignore_cores(machine)

        return self._fill_machine(machine)

    def _fill_machine(self, machine):
        """
        :param ~spinn_machine.Machine machine:
        :param bool repair_machine:
        :param bool ignore_bad_ethernets:
        :rtype: ~spinn_machine.Machine
        """
        for chip_info in sorted(
                self._chip_info.values(), key=lambda chip: (chip.x, chip.y)):
            if (chip_info.ethernet_ip_address is not None and
                    (chip_info.x != chip_info.nearest_ethernet_x
                     or chip_info.y != chip_info.nearest_ethernet_y)):
                if get_config_bool("Machine", "ignore_bad_ethernets"):
                    logger.warning(
                        "Chip {}:{} claimed it has ip address: {}. "
                        "This ip will not be used.",
                        chip_info.x, chip_info.y,
                        chip_info.ethernet_ip_address)
                    chip_info.clear_ethernet_ip_address()
                else:
                    logger.warning(
                        "Not using chip {}:{} as it has an unexpected "
                        "ip address: {}", chip_info.x, chip_info.y,
                        chip_info.ethernet_ip_address)
                    continue

            # If the above has not continued, add the chip
            machine.add_chip(self._make_chip(chip_info, machine))

        machine.validate()
        return machine_repair(machine)

    # Stuff below here is purely for dealing with ignores

    def _process_ignore_links(self, machine):
        """
        Processes the collection of ignore links to remove then from chipinfo.

        Converts any local (x, y, IP address) to global (x, y)

        Discards any ignores which are known to have no
        affect based on the already read chip_info

        Also removes any inverse links

        Logs all actions except for ignores with unused IP addresses

        :param ~spinn_machine.Machine machine:
            An empty machine to handle wrap-arounds
        """
        for ignore in IgnoreLink.parse_string(
                get_config_str("Machine", "down_links")):
            global_xy = self._ignores_local_to_global(
                ignore.x, ignore.y, ignore.ip_address, machine)
            if global_xy is None:
                continue
            chip_info = self._chip_info.get(global_xy, None)
            if chip_info is None:
                self._report_ignore(
                    "Discarding ignore link on chip {} as it is not/ no longer"
                    " in info", global_xy)
                continue
            link = ignore.link
            if link in chip_info.working_links:
                chip_info.working_links.remove(link)
                self._report_ignore(
                    "On chip {} ignoring link:{}", global_xy, link)
                # ignore the inverse link too
                inv_xy = machine.xy_over_link(global_xy[0], global_xy[1], link)
                if inv_xy in self._chip_info:
                    inv_chip_info = self._chip_info[inv_xy]
                    inv_link = (link + 3) % 6
                    if inv_link in inv_chip_info.working_links:
                        inv_chip_info.working_links.remove(inv_link)
                        self._report_ignore(
                            "On chip {} ignoring link {} as it is the inverse "
                            "of link {} on chip {}", inv_xy, inv_link, link,
                            global_xy)
            else:
                self._report_ignore(
                    "Discarding ignore link {} on chip {} as it is not/"
                    "no longer in info", link, global_xy)

    def _preprocess_ignore_cores(self, machine):
        """
        Converts the collection of ignore cores into a map of ignore by x,y.

        Converts any local (x, y, IP address) to global (x, y)

        Discards (with log messages) any ignores which are known to have no
        affect based on the already read chip_info

        Converts any physical  cores to virtual ones.
        Core numbers <= 0 are assumed to be 0 - physical_id

        :param ~spinn_machine.Machine machine:
            An empty machine to handle wrap-arounds
        """
        # Convert by ip to global
        for ignore in IgnoreCore.parse_string(
                get_config_str("Machine", "down_cores")):
            global_xy = self._ignores_local_to_global(
                ignore.x, ignore.y, ignore.ip_address, machine)
            if global_xy is None:
                continue
            p = self._get_virtual_p(global_xy, ignore.p)
            if p is not None:
                self._ignore_cores_map[global_xy].add(p)

    def _preprocess_ignore_chips(self, machine):
        """
        Processes the collection of ignore chips and discards their chipinfo.

        Converts any local (x, y IP address) to global (x, y)

        Discards any ignores which are known to have no
        affect based on the already read chip_info

        Logs all actions except for ignores with unused IP addresses

        :param ~spinn_machine.Machine machine:
            An empty machine to handle wrap-arounds
        """
        for ignore in IgnoreChip.parse_string(
                get_config_str("Machine", "down_chips")):
            # Convert by ip to global
            global_xy = self._ignores_local_to_global(
                ignore.x, ignore.y, ignore.ip_address, machine)
            if global_xy is None:
                continue  # Never on this machine
            chip_info = self._chip_info.pop(global_xy, None)
            if chip_info is None:
                continue  # Already ignored maybe by a dead chip list
            self._report_ignore("Chip {} will be ignored", global_xy)
            for link in chip_info.working_links:
                # ignore the inverse link
                inv_xy = machine.xy_over_link(global_xy[0], global_xy[1], link)
                if inv_xy in self._chip_info:
                    inv_chip_info = self._chip_info[inv_xy]
                    inv_link = (link + 3) % 6
                    if inv_link in inv_chip_info.working_links:
                        inv_chip_info.working_links.remove(inv_link)
                        self._report_ignore(
                            "On chip {} ignoring link {} as it points to "
                            "ignored chip chip {}",
                            inv_xy, inv_link, global_xy)

    def _ignores_local_to_global(self, local_x, local_y, ip_address, machine):
        """
        :param int local_x:
        :param int local_y:
        :param str ip_address:
        :param ~spinn_machine.Machine machine:
        :rtype: tuple(int,int)
        """
        if ip_address is None:
            global_xy = (local_x, local_y)
        else:
            ethernet = self._ethernet_by_ipaddress(ip_address)
            if ethernet is None:
                self._report_ignore(
                    "Ignore with ip:{} will be discarded as no board with "
                    "that ip in this machine", ip_address)
                return None
            global_xy = machine.get_global_xy(
                local_x, local_y, ethernet[0], ethernet[1])
            self._report_ignore(
                "Ignores for local x:{} y:{} and ip:{} map to global {} with "
                "root {}", local_x, local_y, ip_address, global_xy,
                self._chip_info[(0, 0)].ethernet_ip_address)

        if global_xy in self._chip_info:
            return global_xy
        else:
            self._report_ignore(
                "Ignore for global chip {} will be discarded as no such chip "
                "in this machine", global_xy)
            return None

    def _ethernet_by_ipaddress(self, ip_address):
        """
        :param str ip_address:
        :rtype: tuple(int,int)
        """
        if self._ethernets is None:
            self._ethernets = dict()
            for chip_info in self._chip_info.values():
                if chip_info.ethernet_ip_address is not None:
                    self._ethernets[chip_info.ethernet_ip_address] = \
                        (chip_info.x, chip_info.y)
        return self._ethernets.get(ip_address, None)

    def _get_virtual_p(self, xy, p):
        """
        :param tuple(int,int) xy:
        :param int p:
        :rtype: int
        """
        if p > 0:
            self._report_ignore("On chip {} ignoring core {}", xy, p)
            return p
        virtual_map = self._physical_to_virtual_map[xy]
        physical = 0 - p
        if physical >= len(virtual_map) or virtual_map[physical] == 0xFF:
            self._report_ignore(
                "On chip {} physical core {} was not used "
                "so ignore is being discarded.", xy, physical)
            return None
        virtual_p = virtual_map[physical]
        if virtual_p == 0:
            self._report_ignore(
                "On chip {} physical core {} was used as the monitor "
                "so will NOT be ignored", xy, physical)
            return None
        self._report_ignore(
            "On chip {} ignoring core {} as it maps to physical "
            "core {}", xy, virtual_p, physical)
        return virtual_p

    def _report_ignore(self, message, *args):
        """
        Writes the ignore message by either creating or appending the report.

        The implementation choice to reopen the file every time is not the
        fastest but is the cleanest and safest for code that in default
        conditions is never run.

        :param str message:
        """
        full_message = message.format(*args) + "\n"
        report_file = join(UtilsDataView.get_run_dir_path(), REPORT_FILE)
        with open(report_file, "a", encoding="utf-8") as r_file:
            r_file.write(full_message)
