from spinnman.messages.scp.impl.scp_read_memory_request\
    import SCPReadMemoryRequest
from spinnman.messages.scp.impl.scp_read_link_request import SCPReadLinkRequest
from spinnman import constants
from spinnman import exceptions
from spinnman.model.p2p_table import P2PTable
from spinnman.messages.scp.impl.scp_chip_info_request import SCPChipInfoRequest
from spinnman.processes.abstract_multi_connection_process \
    import AbstractMultiConnectionProcess
from spinnman.processes.abstract_process import AbstractProcess

from spinn_machine.processor import Processor
from spinn_machine.router import Router
from spinn_machine.chip import Chip
from spinn_machine.sdram import SDRAM
from spinn_machine.machine import Machine
from spinn_machine.link import Link


class _ChipDetailsReceiver(object):

    def __init__(self, get_machine_process, x, y, link):
        self._get_machine_process = get_machine_process
        self._x = x
        self._y = y
        self._link = link

    def _receive_chip_details(self, scp_read_link_response):
        self._get_machine_process._receive_chip_details_from_link(
            scp_read_link_response, self._x, self._y, self._link)


class GetMachineProcess(AbstractMultiConnectionProcess):
    """ A process for getting the machine details over a set of connections
    """

    def __init__(self, connection_selector, ignore_chips, ignore_cores,
                 max_core_id, max_sdram_size=None):
        """
        :param scamp_connections: The connections to use for the interaction
        :type scamp_connections: iterable of\
                    :py:class:`spinnman.connections.abstract_classes.abstract_connection.AbstractConnection`
        """
        AbstractMultiConnectionProcess.__init__(self, connection_selector)

        self._ignore_chips = ignore_chips
        self._ignore_cores = ignore_cores
        self._max_core_id = max_core_id
        self._max_sdram_size = max_sdram_size

        self._width = None
        self._height = None
        self._boot_x = None
        self._boot_y = None
        self._p2p_column_data = list()

        # A dictionary of (x, y) -> ChipInfo
        self._chip_info = dict()

    def _make_chip(self, chip_info):
        """ Creates a chip from a ChipSummaryInfo structure

        :param chip_info: The ChipSummaryInfo structure to create the chip\
                    from
        :type chip_info: \
                    :py:class:`spinnman.model.chip_info.ChipSummaryInfo`
        :return: The created chip
        :rtype: :py:class:`spinn_machine.chip.Chip`
        """

        # Create the processor list
        processors = list()
        max_core_id = chip_info.n_cores - 1
        if self._max_core_id is not None and max_core_id > self._max_core_id:
            max_core_id = self._max_core_id
        for virtual_core_id in range(max_core_id + 1):

            # Add the core provided it is not to be ignored
            if (self._ignore_cores is None or
                    not self._ignore_cores.is_core(
                        chip_info.x, chip_info.y, virtual_core_id)):
                processors.append(Processor(
                    virtual_core_id, is_monitor=virtual_core_id == 0))

        # Create the router
        links = list()
        for link in chip_info.working_links:
            dest_x, dest_y = chip_info.get_link_destination(link)
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
        if self._width is None:
            self._width = chip_info.width
        if self._height is None:
            self._height = chip_info.height
        if self._boot_x is None:
            self._boot_x = chip_info.x
        if self._boot_y is None:
            self._boot_y = chip_info.y

    def _receive_error(self, request, exception, tracebackinfo):

        # If we get an SCPReadLinkRequest with a
        # SpinnmanUnexpectedResponseCodeException, this is a failed link
        # and so can be ignored
        if (not isinstance(request, SCPReadLinkRequest) or
                not isinstance(
                    exception,
                    exceptions.SpinnmanUnexpectedResponseCodeException)):
            AbstractProcess._receive_error(self, request, exception,
                                           tracebackinfo)

    def get_machine_details(self):

        # Read the machine dimensions
        self._send_request(
            SCPChipInfoRequest(x=255, y=255, with_size=True),
            self._receive_chip_info)
        self._finish()
        self.check_for_error()

        # Get the P2P table - 8 entries are packed into each 32-bit word
        p2p_column_bytes = P2PTable.get_n_column_bytes(self._height)
        for column in range(self._width):
            offset = P2PTable.get_column_offset(column)
            self._send_request(
                SCPReadMemoryRequest(
                    x=255, y=255,
                    base_address=(
                        constants.ROUTER_REGISTER_P2P_ADDRESS + offset),
                    size=p2p_column_bytes),
                self._receive_p2p_data)
        self._finish()
        self.check_for_error()
        p2p_table = P2PTable(self._width, self._height, self._p2p_column_data)

        # Get the chip information for each chip
        for (x, y) in p2p_table.iterchips():
            if (x, y) not in self._chip_info:
                self._send_request(
                    SCPChipInfoRequest(x, y), self._receive_chip_info)
        self._finish()
        self.check_for_error()

        # Build a Machine
        chips = [
            self._make_chip(chip_info)
            for chip_info in self._chip_info.itervalues()]
        machine = Machine(chips, self._boot_x, self._boot_y)

        return machine

    def get_chip_info(self):
        """ Get the chip information for the machine.  Note that\
            get_machine_details must have been called first
        """
        return self._chip_info
