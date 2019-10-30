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

from collections import defaultdict
import logging
import functools
from spinn_utilities.log import FormatAdapter
from spinn_machine import (
    Router, Chip, SDRAM, Link, machine_from_size)
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


class GetMachineProcess(AbstractMultiConnectionProcess):
    """ A process for getting the machine details over a set of connections.
    """
    __slots__ = [
        "_chip_info",
        # Used if there are any ignores with ip addresses
        # Holds a mapping from ip to board root (x,y)
        "_ethernets",
        "_ignore_chips",
        "_ignore_cores",
        # Holds a map from x,y to a list of virtual cores to ignores
        "_ignore_cores_map",
        "_ignore_links",
        "_max_sdram_size",
        "_p2p_column_data",
        # Used if there are any ignore core requests
        # Holds a mapping from (x,y) to a mapping of phsyical to virtual core
        "_virtual_map"]

    def __init__(self, connection_selector, ignore_chips, ignore_cores,
                 ignore_links, max_sdram_size=None):
        # pylint: disable=too-many-arguments
        super(GetMachineProcess, self).__init__(connection_selector)

        self._ignore_chips = ignore_chips if ignore_chips is not None else {}
        self._ignore_cores = ignore_cores if ignore_cores is not None else {}
        self._ignore_links = ignore_links if ignore_links is not None else {}

        self._max_sdram_size = max_sdram_size

        self._p2p_column_data = list()

        # A dictionary of (x, y) -> ChipInfo
        self._chip_info = dict()

        # Set ethernets to None meaning not computed yet
        self._ethernets = None
        self._virtual_map = {}

    def _make_chip(self, chip_info, machine):
        """ Creates a chip from a ChipSummaryInfo structure.

        :param chip_info: \
            The ChipSummaryInfo structure to create the chip from
        :type chip_info: \
            :py:class:`spinnman.model.ChipSummaryInfo`
        :return: The created chip
        :rtype: :py:class:`spinn_machine.Chip`
        """

        # Create the down cores set if any
        n_cores = min(chip_info.n_cores, Machine.max_cores_per_chip())
        core_states = chip_info.core_states
        down_cores = self._ignore_cores_map.get(
            (chip_info.x, chip_info.y))
        for i in range(1, n_cores):
            if core_states[i] != CPUState.IDLE:
                logger.warning(
                    "Not using core {}, {}, {} in state {}",
                    chip_info.x, chip_info.y, i,  core_states[i])
                if down_cores is None:
                    down_cores = set()
                down_cores.add(i)

        # Create the router
        router = self._make_router(chip_info, machine)

        # Create the chip's SDRAM object
        sdram_size = chip_info.largest_free_sdram_block
        if (self._max_sdram_size is not None and
                sdram_size > self._max_sdram_size):
            sdram_size = self._max_sdram_size
        sdram = SDRAM(size=sdram_size)

        # Create the chip
        return Chip(
            x=chip_info.x, y=chip_info.y, n_processors=n_cores,
            router=router, sdram=sdram,
            ip_address=chip_info.ethernet_ip_address,
            nearest_ethernet_x=chip_info.nearest_ethernet_x,
            nearest_ethernet_y=chip_info.nearest_ethernet_y,
            down_cores=down_cores)

    def _make_router(self, chip_info, machine):
        links = list()
        for link in chip_info.working_links:
            dest = machine.xy_over_link(chip_info.x, chip_info.y, link)
            if ((chip_info.x, chip_info.y, link) not in self._ignore_links
                    and dest not in self._ignore_chips
                    and dest in self._chip_info):
                dest_x, dest_y = dest
                links.append(Link(
                    chip_info.x, chip_info.y, link, dest_x, dest_y))
        return Router(
            links=links,
            n_available_multicast_entries=(
                chip_info.n_free_multicast_routing_entries))

    def _receive_p2p_data(self, column, scp_read_response):
        self._p2p_column_data[column] = (
            scp_read_response.data, scp_read_response.offset)

    def _receive_chip_info(self, scp_read_chip_info_response):
        chip_info = scp_read_chip_info_response.chip_info
        self._chip_info[chip_info.x, chip_info.y] = chip_info

    def _receive_error(self, request, exception, tb):
        # If we get an ReadLink with a
        # SpinnmanUnexpectedResponseCodeException, this is a failed link
        # and so can be ignored
        if isinstance(request, ReadLink):
            if isinstance(exception, SpinnmanUnexpectedResponseCodeException):
                return
        super(GetMachineProcess, self)._receive_error(request, exception, tb)

    def get_machine_details(self, boot_x, boot_y, width, height,
                            repair_machine, ignore_bad_ethernets):

        machine = machine_from_size(width, height)
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
                functools.partial(self._receive_p2p_data, column))
        self._finish()
        self.check_for_error()
        p2p_table = P2PTable(width, height, self._p2p_column_data)

        # Get the chip information for each chip
        for (x, y) in p2p_table.iterchips():
            self._send_request(GetChipInfo(x, y), self._receive_chip_info)
        self._finish()
        try:
            self.check_for_error()
        except Exception:  # pylint: disable=broad-except
            # Ignore errors so far, as any error here just means that a chip
            # is down that wasn't marked as down
            pass

        # Warn about unexpected missing chips
        for (x, y) in p2p_table.iterchips():
            if (x, y) not in self._chip_info:
                logger.warning(
                    "Chip {}, {} was expected but didn't reply", x, y)

        self._preprocess_ignore_cores(machine)
        self._preprocess_ignore_chips(machine)

        return self._fill_machine(
            machine, repair_machine, ignore_bad_ethernets)

    def _fill_machine(
            self, machine, repair_machine, ignore_bad_ethernets):
        for chip_info in sorted(
                self._chip_info.values(), key=lambda chip: (chip.x, chip.y)):
            if (chip_info.x, chip_info.y) in self._ignore_chips:
                logger.warning(
                    "Not using chip {}, {} as in the ignore list",
                    chip_info.x, chip_info.y)
                continue
            if (chip_info.ethernet_ip_address is not None and
                    (chip_info.x != chip_info.nearest_ethernet_x
                     or chip_info.y != chip_info.nearest_ethernet_y)):
                if ignore_bad_ethernets:
                    logger.warning(
                        "Chip {}:{} claimed it has ip address: {}. "
                        "This ip will not be used.",
                        chip_info.x, chip_info.y,
                        chip_info.ethernet_ip_address)
                    chip_info.ethernet_ip_address = None
                else:
                    logger.warning(
                        "Not using chip {}:{} as it has an unexpected "
                        "ip address: {}", chip_info.x, chip_info.y,
                        chip_info.ethernet_ip_address)
                    continue
            else:
                machine.add_chip(self._make_chip(chip_info, machine))

        machine.validate()
        return machine_repair(machine, repair_machine)

    def get_chip_info(self):
        """ Get the chip information for the machine.

        .. note::
            :py:meth:`get_machine_details` must have been called first.
        """
        return self._chip_info

    # Stuff below here is purely for dealing with ignores

    def _preprocess_ignore_cores(self, machine):
        self._ignore_cores_map = defaultdict(set)
        if len(self._ignore_cores) == 0:
            return
        # Convert by ip to global
        for ignore in self._ignore_cores:
            local_x = ignore[0]
            local_y = ignore[0]
            if len(ignore) > 3:
                ip = ignore[3]
            else:
                ip = None
            global_xy = self._ignores_local_to_global(
                local_x, local_y, ip, machine)
            if global_xy is None:
                continue
            global_x = global_xy[0]
            global_y = global_xy[1]
            p = self._get_virtual_p(global_x, global_y, ignore[2])
            if p is not None:
                self._ignore_cores_map[(global_x, global_y)].add(p)

    def _preprocess_ignore_chips(self, machine):
        if len(self._ignore_cores) == 0:
            return
        new_ignores = set()
        # Convert by ip to global
        for ignore in self._ignore_chips:
            local_x = ignore[0]
            local_y = ignore[0]
            if len(ignore) > 2:
                ip = ignore[2]
            else:
                ip = None
            global_xy = self._ignores_local_to_global(
                local_x, local_y, ip, machine)
            if global_xy is None:
                continue
            else:
                new_ignores.add((global_xy[0], global_xy[1]))
        self._ignore_chips = new_ignores

    def _ignores_local_to_global(self, local_x, local_y, ip_address, machine):
        if ip_address is None:
            global_x = local_x
            global_y = local_y
        else:
            ethernet = self._ethernet_by_ipaddress(ip_address)
            if ethernet is None:
                logger.info("Ignore with ip:{} will be discarded "
                            "as board with that ip in this machine",
                            ip_address)
                return None
            global_x, global_y = machine.get_global_xy(
                local_x, local_y, ethernet[0], ethernet[1])
            logger.info("Ignores for local x:{} y:{} and ip:{} "
                        "map to global x:{} y:{} with root {}",
                        local_x, local_y, ip_address,
                        global_x, global_y,
                        self._chip_info[(0, 0)].ethernet_ip_address)

        if (global_x, global_y) in self._chip_info:
            return (global_x, global_y)
        else:
            logger.info("Ignore with x:{} and y:{} will be discarded "
                        "as no such chip in this machine",
                        global_x, global_y)
            return None

    def _ethernet_by_ipaddress(self, ip_address):
        if self._ethernets is None:
            self._ethernets = dict()
            for chip_info in self._chip_info.values():
                if chip_info.ethernet_ip_address is not None:
                    self._ethernets[chip_info.ethernet_ip_address] = \
                        (chip_info.x, chip_info.y)
        return self._ethernets.get(ip_address, None)

    def _get_virtual_p(self, x, y, p):
        if (x, y) not in self._virtual_map:
            if (x, y) not in self._chip_info:
                # Chip not part of board so ignore
                return None
            p_to_v = SystemVariableDefinition.physical_to_virtual_core_map
            self._send_request(
                ReadMemory(
                    x=x, y=y,
                    base_address=(
                            SYSTEM_VARIABLE_BASE_ADDRESS + p_to_v.offset),
                    size=p_to_v.array_size),
                    functools.partial(
                        self._receive_physical_to_virtual_core_map, x, y))
            self._finish()

        if p > 0:
            return p
        else:
            virtual_map = self._virtual_map[(x, y)]
            if 0-p not in virtual_map:
                logger.warning(
                    "Physical core {}:{}:{} was not used "
                    "so ignore is being discarded.".format(x, y, -p))
                return None
            virtual_p = virtual_map[0-p]
            if virtual_p == 0:
                logger.warning(
                    "Physical core {}:{}:{} was used as the monitor "
                    "so will NOT be ignored".format(x, y, -p))
                return None
            logger.info("Ignoring core {}:{}:{} as it maps to physical core {}",
                        x, y, 0-p, virtual_p)
            return virtual_p

    def _receive_physical_to_virtual_core_map(self, x, y, scp_read_response):
        chipinfo = self._chip_info[(x, y)]
        ip_address = self._chip_info[(0, 0)].ethernet_ip_address

        logger.info("Received physical_to_virtual_core_map for {}:{} for {}"
                    "", x, y, ip_address)
        p_to_v_map = {}

        for i in range(
                scp_read_response.offset,
                scp_read_response.offset + chipinfo.n_cores):
            p_to_v_map[i-scp_read_response.offset] = \
                int(scp_read_response.data[i])
        logger.info("{}", p_to_v_map)  # logger formats so dict as a param
        self._virtual_map[(x, y)] = p_to_v_map

    def _verify__virtual_to_physical_core_map(self, x, y):
        """ Add this method to _get_virtual_p to verify the mappings"""
        v_to_p = SystemVariableDefinition.virtual_to_physical_core_map
        self._send_request(
            ReadMemory(
            x=x, y=y,
            base_address=(
                    SYSTEM_VARIABLE_BASE_ADDRESS + v_to_p.offset),
            size=v_to_p.array_size),
            functools.partial(
                self._receive_virtual_to_physical_core_map, x, y))
        self._finish()

    def _receive_virtual_to_physical_core_map(self, x, y, scp_read_response):
        p_to_v_map = self._virtual_map[(x, y)]
        chipinfo = self._chip_info[(x, y)]
        for i in range(
                scp_read_response.offset,
                scp_read_response.offset + chipinfo.n_cores):
            assert p_to_v_map[int(scp_read_response.data[i])] == \
                    i-scp_read_response.offset
        logger.info("Virtual_to_physical_core_map checks for {}:{}", x, y)

