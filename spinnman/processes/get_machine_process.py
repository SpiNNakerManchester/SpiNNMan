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

import logging
import functools
from spinn_utilities.log import FormatAdapter
from spinn_machine import (
    Processor, Router, Chip, SDRAM, Link, machine_from_size)
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
        "_ethernets",
        "_ignore_chips",
        "_ignore_cores",
        "_ignore_links",
        "_max_sdram_size",
        "_p2p_column_data",
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

        # Create the processor list
        n_cores = min(chip_info.n_cores, Machine.max_cores_per_chip())
        #core_states = chip_info.core_states
        if len(self._ignore_cores) > 0:
            raise NotImplementedError("ignore_cores currently not implemented")
        #            logger.warning(
        #                "Not using core {}, {}, {} in state {}",
        #                chip_info.x, chip_info.y, virtual_core_id,
        #                core_states[virtual_core_id])

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
            nearest_ethernet_y=chip_info.nearest_ethernet_y)

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

    def _receive_virtual_to_physical_core_map(self, x, y, scp_read_response):
        p_to_v_map = self._virtual_map[(x, y)]
        chipinfo = self._chip_info[(x, y)]
        for i in range(
                scp_read_response.offset,
                scp_read_response.offset + chipinfo.n_cores):
            assert p_to_v_map[int(scp_read_response.data[i])] == \
                    i-scp_read_response.offset
        logger.info("Virtual_to_physical_core_map checks for {}:{}", x, y)

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
            # Optional assert the mapping back the other way
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

        return p
        if p > 0:
            return p
        else:
            return self._virtual_map[(x, y)][0-p]

    def _preprocess_ignore_cores(self, width, height):
        if len(self._ignore_cores) == 0:
            return
        temp_machine = machine_from_size(width, height)
        new_ignores = []
        # Convert by ip to global
        for ignore in self._ignore_cores:
            if len(ignore) > 3:
                ip_address = ignore[3]
                ethernet = self._ethernet_by_ipaddress(ip_address)
                if ethernet is not None:
                    global_x, global_y = temp_machine.get_global_xy(
                        ignore[0], ignore[1], ethernet[0], ethernet[1])
                    p = self._get_virtual_p(global_x, global_y, ignore[2])
            else:
                p = self._get_virtual_p(ignore[0], ignore[1], ignore[2])

        # Get physical virtual map

        # HACK remove ignore cores we can handle
        self._ignore_cores = []

    def get_machine_details(self, boot_x, boot_y, width, height,
                            repair_machine, ignore_bad_ethernets):

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

        self._preprocess_ignore_cores(width, height)

        return self.create_machine(
            width, height, repair_machine, ignore_bad_ethernets)

    def create_machine(
            self, width, height, repair_machine, ignore_bad_ethernets):
        bad_ethernets = []
        machine = machine_from_size(width, height)
        for chip_info in sorted(
                self._chip_info.values(), key=lambda chip: (chip.x, chip.y)):
            if (chip_info.x, chip_info.y) not in self._ignore_chips:
                if (chip_info.ethernet_ip_address is not None and
                    (chip_info.x != chip_info.nearest_ethernet_x
                     or chip_info.y != chip_info.nearest_ethernet_y)):
                    bad_ethernets.append(
                        (chip_info, chip_info.ethernet_ip_address))
                    if ignore_bad_ethernets:
                        # pylint: disable=protected-access
                        chip_info._ethernet_ip_address = None
                        machine.add_chip(
                            self._make_chip(chip_info, machine))
                else:
                    machine.add_chip(self._make_chip(chip_info, machine))

        removed_chips = []
        if len(bad_ethernets) > 0:
            msg = ""
            for chip_info, claim in bad_ethernets:
                chip = self._make_chip(chip_info, machine)
                local_x, local_y = machine.get_local_xy(chip)
                ethernet = machine.get_chip_at(
                    chip.nearest_ethernet_x, chip.nearest_ethernet_y)
                msg += "x:{} y:{} on board:{} claims it has ethernet {} " \
                       "".format(local_x, local_y, ethernet.ip_address, claim)
                removed_chips.append((chip.x, chip.y))
            logger.warning(msg)

            if ignore_bad_ethernets:
                # No chips actually removed
                removed_chips = []
        machine.validate()
        return machine_repair(machine, repair_machine, removed_chips)

    def get_chip_info(self):
        """ Get the chip information for the machine.

        .. note::
            :py:meth:`get_machine_details` must have been called first.
        """
        return self._chip_info
