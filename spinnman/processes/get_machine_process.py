import logging

from spinn_machine import Processor, Router, Chip, SDRAM, Machine, Link

from spinnman.constants import ROUTER_REGISTER_P2P_ADDRESS
from spinnman.exceptions import SpinnmanUnexpectedResponseCodeException
from spinnman.messages.scp.impl \
    import ReadMemory, ReadLink, GetChipInfo
from spinnman.model import P2PTable
from spinnman.model.enums import CPUState
from .abstract_multi_connection_process import AbstractMultiConnectionProcess
from .abstract_process import AbstractProcess

logger = logging.getLogger(__name__)


class GetMachineProcess(AbstractMultiConnectionProcess):
    """ A process for getting the machine details over a set of connections
    """

    def __init__(self, connection_selector, ignore_chips, ignore_cores,
                 ignore_links, max_core_id, max_sdram_size=None):
        AbstractMultiConnectionProcess.__init__(self, connection_selector)

        self._ignore_chips = ignore_chips if ignore_chips is not None else {}
        self._ignore_cores = ignore_cores if ignore_cores is not None else {}
        self._ignore_links = ignore_links if ignore_links is not None else {}
        self._max_core_id = max_core_id
        self._max_sdram_size = max_sdram_size

        self._p2p_column_data = list()

        # A dictionary of (x, y) -> ChipInfo
        self._chip_info = dict()

    def _make_chip(self, width, height, chip_info):
        """ Creates a chip from a ChipSummaryInfo structure

        :param chip_info: The ChipSummaryInfo structure to create the chip\
                    from
        :type chip_info: \
                    :py:class:`spinnman.model.ChipSummaryInfo`
        :return: The created chip
        :rtype: :py:class:`spinn_machine.Chip`
        """

        # Create the processor list
        processors = list()
        max_core_id = chip_info.n_cores - 1
        core_states = chip_info.core_states
        if self._max_core_id is not None and max_core_id > self._max_core_id:
            max_core_id = self._max_core_id
        for virtual_core_id in range(max_core_id + 1):

            # Add the core provided it is not to be ignored
            if ((chip_info.x, chip_info.y, virtual_core_id) not in
                    self._ignore_cores):
                if virtual_core_id == 0:
                    processors.append(Processor(
                        virtual_core_id, is_monitor=True))
                elif core_states[virtual_core_id] == CPUState.IDLE:
                    processors.append(Processor(virtual_core_id))
                else:
                    logger.warn("Not using core {}, {}, {} in state {}".format(
                        chip_info.x, chip_info.y, virtual_core_id,
                        core_states[virtual_core_id]))

        # Create the router
        links = list()
        for link in chip_info.working_links:
            dest_x, dest_y = Machine.get_chip_over_link(
                chip_info.x, chip_info.y, link, width, height)
            if ((chip_info.x, chip_info.y, link) not in self._ignore_links and
                    (dest_x, dest_y) not in self._ignore_chips and
                    (dest_x, dest_y) in self._chip_info):
                opposite_link_id = (link + 3) % 6
                links.append(Link(
                    chip_info.x, chip_info.y, link, dest_x, dest_y,
                    opposite_link_id, opposite_link_id))
        router = Router(
            links=links,
            n_available_multicast_entries=(
                chip_info.n_free_multicast_routing_entries))

        # Create the chip's SDRAM object
        sdram_size = chip_info.largest_free_sdram_block
        if (self._max_sdram_size is not None and
                sdram_size > self._max_sdram_size):
            sdram_size = self._max_sdram_size
        sdram = SDRAM(size=sdram_size)

        # Create the chip
        chip = Chip(
            x=chip_info.x, y=chip_info.y, processors=processors,
            router=router, sdram=sdram,
            ip_address=chip_info.ethernet_ip_address,
            nearest_ethernet_x=chip_info.nearest_ethernet_x,
            nearest_ethernet_y=chip_info.nearest_ethernet_y)

        return chip

    def _receive_p2p_data(self, scp_read_response):
        self._p2p_column_data.append(
            (scp_read_response.data, scp_read_response.offset))

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
        AbstractProcess._receive_error(self, request, exception, tb)

    def get_machine_details(self, boot_x, boot_y, width, height):
        # Get the P2P table - 8 entries are packed into each 32-bit word
        p2p_column_bytes = P2PTable.get_n_column_bytes(height)
        for column in range(width):
            offset = P2PTable.get_column_offset(column)
            self._send_request(
                ReadMemory(
                    x=boot_x, y=boot_y,
                    base_address=(ROUTER_REGISTER_P2P_ADDRESS + offset),
                    size=p2p_column_bytes),
                self._receive_p2p_data)
        self._finish()
        self.check_for_error()
        p2p_table = P2PTable(width, height, self._p2p_column_data)

        # Get the chip information for each chip
        for (x, y) in p2p_table.iterchips():
            self._send_request(
                GetChipInfo(x, y), self._receive_chip_info)
        self._finish()
        try:
            self.check_for_error()
        except:
            # Ignore errors so far, as any error here just means that a chip
            # is down that wasn't marked as down
            pass

        # Warn about unexpected missing chips
        for (x, y) in p2p_table.iterchips():
            if (x, y) not in self._chip_info:
                logger.warn("Chip {}, {} was expected but didn't reply".format(
                    x, y))

        # Build a Machine
        def chip_xy(chip):
            return chip.x, chip.y

        chips = [
            self._make_chip(width, height, chip_info)
            for chip_info in sorted(self._chip_info.values(), key=chip_xy)
            if (chip_info.x, chip_info.y) not in self._ignore_chips]
        machine = Machine(chips, boot_x, boot_y)

        return machine

    def get_chip_info(self):
        """ Get the chip information for the machine.  Note that\
            get_machine_details must have been called first
        """
        return self._chip_info
