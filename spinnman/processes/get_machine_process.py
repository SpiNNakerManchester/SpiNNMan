from spinnman.model.chip_info import ChipInfo
from spinnman.messages.scp.impl.scp_read_memory_request\
    import SCPReadMemoryRequest
from spinnman.messages.scp.impl.scp_read_link_request import SCPReadLinkRequest
from spinnman import constants
from spinnman.exceptions import SpinnmanUnexpectedResponseCodeException
from spinnman.processes.abstract_multi_connection_process \
    import AbstractMultiConnectionProcess
from spinnman.processes.abstract_process import AbstractProcess

from spinn_machine.processor import Processor
from spinn_machine.router import Router
from spinn_machine.chip import Chip
from spinn_machine.sdram import SDRAM
from spinn_machine.machine import Machine
from spinn_machine.link import Link

from collections import deque
import traceback


class _ChipInfoReceiver(object):

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

    def __init__(self, scamp_connections, ignore_chips, ignore_cores,
                 max_core_id):
        """
        :param scamp_connections: The connections to use for the interaction
        :type scamp_connections: iterable of\
                    :py:class:`spinnman.connections.abstract_classes.abstract_connection.AbstractConnection`
        """
        AbstractMultiConnectionProcess.__init__(self, scamp_connections)

        self._ignore_chips = ignore_chips
        self._ignore_cores = ignore_cores
        self._max_core_id = max_core_id

        # A dictionary of (x, y) -> ChipInfo
        self._chip_info = dict()

        # The machine so far
        self._machine = Machine([])

        # A dictionary of which link goes where from a chip:
        # (x, y, link) -> (x, y)
        self._link_destination = dict()

        # A queue of ChipInfo to be examined
        self._search = deque()

    def _make_chip(self, chip_details):
        """ Creates a chip from a ChipInfo structure

        :param chip_details: The ChipInfo structure to create the chip\
                    from
        :type chip_details: \
                    :py:class:`spinnman.model.chip_info.ChipInfo`
        :return: The created chip
        :rtype: :py:class:`spinn_machine.chip.Chip`
        """

        # Create the processor list
        processors = list()
        for virtual_core_id in chip_details.virtual_core_ids:
            if (self._ignore_cores is not None and
                    self._ignore_cores.is_core(
                        chip_details.x, chip_details.y, virtual_core_id)):
                continue
            if (self._max_core_id is not None and
                    virtual_core_id > self._max_core_id):
                continue

            processors.append(Processor(
                virtual_core_id, chip_details.cpu_clock_mhz * 1000000,
                virtual_core_id == 0))

        # Create the router - add the links later during search
        router = Router(
            links=list(), emergency_routing_enabled=False,
            clock_speed=Router.ROUTER_DEFAULT_CLOCK_SPEED,
            n_available_multicast_entries=(
                Router.ROUTER_DEFAULT_AVAILABLE_ENTRIES -
                chip_details.first_free_router_entry))

        # Create the chip
        chip = Chip(
            x=chip_details.x, y=chip_details.y, processors=processors,
            router=router, sdram=SDRAM(
                user_base_address=chip_details.sdram_base_address,
                system_base_address=chip_details.system_sdram_base_address),
            ip_address=chip_details.ip_address,
            nearest_ethernet_x=chip_details.nearest_ethernet_x,
            nearest_ethernet_y=chip_details.nearest_ethernet_y)
        return chip

    def _receive_chip_details(self, scp_read_memory_response):
        try:
            new_chip_details = ChipInfo(scp_read_memory_response.data,
                                        scp_read_memory_response.offset)
            if (self._ignore_chips is not None and
                    self._ignore_chips.is_chip(
                        new_chip_details.x, new_chip_details.y)):
                return None
            key = (new_chip_details.x, new_chip_details.y)
            if key not in self._chip_info:
                self._chip_info[key] = new_chip_details
                self._search.append(new_chip_details)
                new_chip = self._make_chip(new_chip_details)
                self._machine.add_chip(new_chip)
                return new_chip
            return self._machine.get_chip_at(new_chip_details.x,
                                             new_chip_details.y)
        except Exception:
            traceback.print_exc()

    def _receive_chip_details_from_link(self, scp_read_link_response,
                                        source_x, source_y, link):
        new_chip = self._receive_chip_details(scp_read_link_response)
        if new_chip is not None:
            self._link_destination[(source_x, source_y, link)] = new_chip

    def _receive_error(self, request, exception, tracebackinfo):

        # If we get an SCPReadLinkRequest with a
        # SpinnmanUnexpectedResponseCodeException, this is a failed link
        # and so can be ignored
        if (not isinstance(request, SCPReadLinkRequest) or
                not isinstance(exception,
                               SpinnmanUnexpectedResponseCodeException)):
            AbstractProcess._receive_error(self, request, exception,
                                           tracebackinfo)

    def get_machine_details(self):

        # Get the details of chip 0, 0
        self._send_request(
            SCPReadMemoryRequest(
                x=0, y=0, base_address=constants.SYSTEM_VARIABLE_BASE_ADDRESS,
                size=constants.SYSTEM_VARIABLE_BYTES),
            self._receive_chip_details,
            self._receive_error)
        self._finish()

        # Continue until there is nothing to search (and no exception)
        while not self.is_error() and len(self._search) > 0:

            # Set up the next round of searches using everything that
            # needs to search (same loop as above, I know, but wait for it)
            while not self.is_error() and len(self._search) > 0:
                chip_info = self._search.pop()

                # Examine the links of the chip to find the next chips
                for link in chip_info.links_available:

                    # Add the read_link request - note that this might
                    # add to the search if a response is received
                    receiver = _ChipInfoReceiver(self, chip_info.x,
                                                 chip_info.y, link)
                    self._send_request(
                        SCPReadLinkRequest(
                            x=chip_info.x, y=chip_info.y, cpu=0, link=link,
                            base_address=(constants
                                          .SYSTEM_VARIABLE_BASE_ADDRESS),
                            size=constants.SYSTEM_VARIABLE_BYTES),
                        receiver._receive_chip_details,
                        self._receive_error)

            # Ensure all responses up to this point have been received
            self._finish()

        # If there is an exception, raise it
        self.check_for_error()

        # We now have all the chip details, now link them up and make a machine
        # Start by making a queue of (chip, link ids) to search, starting at
        # 0, 0
        chip_0_0_info = self._chip_info[(0, 0)]
        chip_0_0 = self._machine.get_chip_at(0, 0)
        chip_search = deque([(chip_0_0, chip_0_0_info.links_available)])

        # Go through the chips, link by link
        seen_chips = set()
        seen_chips.add((0, 0))
        while len(chip_search) > 0:
            chip, links = chip_search.pop()

            # Go through the links of the chip
            for link in links:

                # Only continue if the chip link worked
                if (chip.x, chip.y, link) in self._link_destination:

                    other_chip = self._link_destination[(chip.x, chip.y, link)]

                    # Standard links use the opposite link id (with ids between
                    # 0 and 5) as default
                    opposite_link_id = (link + 3) % 6

                    # Check that the other chip link worked in reverse
                    if ((other_chip.x, other_chip.y, opposite_link_id) in
                            self._link_destination):

                        # Add the link to this chip
                        chip.router.add_link(Link(
                            chip.x, chip.y, link, other_chip.x, other_chip.y,
                            opposite_link_id, opposite_link_id))

                        # If the chip is not already seen, add it to the search
                        if (other_chip.x, other_chip.y) not in seen_chips:
                            other_chip_details = self._chip_info[
                                (other_chip.x, other_chip.y)]
                            chip_search.append((
                                other_chip,
                                other_chip_details.links_available))
                            seen_chips.add((other_chip.x, other_chip.y))

        return self._machine

    def get_chip_info(self):
        """ Get the chip information for the machine.  Note that\
            get_machine_details must have been called first
        """
        return self._chip_info
