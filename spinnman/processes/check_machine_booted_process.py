from spinn_machine.utilities.progress_bar import ProgressBar
from spinnman import constants
from spinnman.messages.scp.scp_result import SCPResult
from spinnman.model.chip_info import ChipInfo
from spinnman.messages.scp.impl.scp_read_link_request import SCPReadLinkRequest
from spinnman.messages.scp.impl.scp_version_request import SCPVersionRequest
from spinnman.exceptions import SpinnmanTimeoutException
from spinnman.messages.scp.impl.scp_read_memory_request \
    import SCPReadMemoryRequest

from spinn_machine.machine import Machine
from spinn_machine.processor import Processor
from spinn_machine.router import Router
from spinn_machine.chip import Chip
from spinn_machine.sdram import SDRAM
from spinn_machine.link import Link

from collections import deque
from collections import OrderedDict

import logging
import time

logger = logging.getLogger(__file__)


class CheckMachineBootedProcess(object):

    def __init__(
            self, connection, ignore_chips, ignore_cores, max_core_id,
            max_sdram_size):
        self._connection = connection
        self._ignore_chips = ignore_chips
        self._ignore_cores = ignore_cores
        self._max_core_id = max_core_id
        self._max_sdram_size = max_sdram_size

    def _send(self, request):
        response = request.get_scp_response()
        retries = 3
        result = None
        while retries > 0 and (result is None or result != SCPResult.RC_OK):
            try:
                self._connection.send_scp_request(request)
                result, _, data, offset = \
                    self._connection.receive_scp_response()
                if result == SCPResult.RC_OK:
                    response.read_bytestring(data, offset)
                    return result, response
                retries -= 1
            except SpinnmanTimeoutException:
                retries -= 1
        return result, None

    def _read_version(self, x, y):
        result, version_response = self._send(SCPVersionRequest(x, y, 0))
        if version_response is not None:
            return result, version_response.version_info
        return result, None

    def _read_chip_data(self, read_request):
        result, read_response = self._send(read_request)
        if read_response is not None:
            return result, ChipInfo(read_response.data, read_response.offset)
        return result, None

    def _read_chip(self, x, y):
        read_request = SCPReadMemoryRequest(
            x=x, y=y, base_address=constants.SYSTEM_VARIABLE_BASE_ADDRESS,
            size=constants.SYSTEM_VARIABLE_BYTES)
        return self._read_chip_data(read_request)

    def _read_chip_down_link(self, x, y, link):
        read_request = SCPReadLinkRequest(
            x=x, y=y, link=link,
            base_address=constants.SYSTEM_VARIABLE_BASE_ADDRESS,
            size=constants.SYSTEM_VARIABLE_BYTES)
        return self._read_chip_data(read_request)

    def _add_chip(self, machine, chip_details, link_destination):

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

        # Create the router
        router = Router(
            links=list(), emergency_routing_enabled=False,
            clock_speed=Router.ROUTER_DEFAULT_CLOCK_SPEED,
            n_available_multicast_entries=(
                Router.ROUTER_DEFAULT_AVAILABLE_ENTRIES -
                chip_details.first_free_router_entry))

        # Go through the links of the chip
        for link in chip_details.links_available:

            # Only continue if the chip link worked
            if (chip_details.x, chip_details.y,
                    link) in link_destination:

                other_x, other_y = link_destination[
                    (chip_details.x, chip_details.y, link)]

                # Standard links use the opposite link id (with ids between
                # 0 and 5) as default
                opposite_link_id = (link + 3) % 6

                # Check that the other chip link worked in reverse
                if (other_x, other_y, opposite_link_id) in link_destination:

                    # Add the link to this chip
                    router.add_link(Link(
                        chip_details.x, chip_details.y, link, other_x,
                        other_y, opposite_link_id, opposite_link_id))

        # Create the chip's SDRAM object
        sdram = None
        if self._max_sdram_size is not None:
            size = (chip_details.system_sdram_base_address -
                    chip_details.sdram_heap_address)
            if size > self._max_sdram_size:
                system_base_address = \
                    chip_details.sdram_heap_address + self._max_sdram_size
                sdram = SDRAM(
                    user_base_address=chip_details.sdram_heap_address,
                    system_base_address=system_base_address)
            else:
                sdram = SDRAM(
                    user_base_address=chip_details.sdram_heap_address,
                    system_base_address=chip_details.system_sdram_base_address)
        else:
            sdram = SDRAM(
                user_base_address=chip_details.sdram_heap_address,
                system_base_address=chip_details.system_sdram_base_address)

        # Create the chip
        chip = Chip(
            x=chip_details.x, y=chip_details.y, processors=processors,
            router=router, sdram=sdram,
            ip_address=chip_details.ip_address,
            nearest_ethernet_x=chip_details.nearest_ethernet_x,
            nearest_ethernet_y=chip_details.nearest_ethernet_y)

        machine.add_chip(chip)

    def check_machine_is_booted(self):

        # Check that chip 0, 0 is booted
        result, chip_0_0_data = self._read_chip(0, 0)
        if chip_0_0_data is None:
            logger.error("Could not read from 0, 0: {}", result)
            return None, None

        progress_bar = ProgressBar(
            float(chip_0_0_data.x_size * chip_0_0_data.y_size * 2),
            "Verifying Machine")

        # Go through the chips, link by link
        chip_search = deque([chip_0_0_data])
        seen_chips = OrderedDict({(0, 0): chip_0_0_data})
        link_destination = dict()
        while len(chip_search) > 0:
            chip = chip_search.pop()
            details = seen_chips[chip.x, chip.y]

            for link in range(0, 6):
                chip_data = None
                retries = 3
                while chip_data is None and retries > 0:
                    _, chip_data = self._read_chip_down_link(
                        chip.x, chip.y, link)
                    if chip_data is not None and (
                            self._ignore_chips is None or
                            not self._ignore_chips.is_chip(
                                chip_data.x, chip_data.y)):
                        link_destination[(chip.x, chip.y, link)] = (
                            chip_data.x, chip_data.y)
                        if (chip_data.x, chip_data.y) not in seen_chips:
                            chip_search.append(chip_data)
                            seen_chips[(chip_data.x, chip_data.y)] = chip_data
                            progress_bar.update()
                    elif link in details.links_available:
                        retries -= 1
                        time.sleep(0.2)
                    else:
                        retries = 0

        # Try to read each found chip
        machine = Machine([])
        for x, y in seen_chips:
            if (self._ignore_chips is None or
                    not self._ignore_chips.is_chip(x, y)):

                # Retry up to 3 times
                retries = 3
                result = None
                chip_details = None
                while retries > 0:
                    result, chip_details = self._read_chip(x, y)
                    if chip_details is not None:
                        self._add_chip(machine, chip_details, link_destination)
                        progress_bar.update()
                        break

                    # Wait between retries
                    time.sleep(0.5)
                    retries -= 1

                # If no version could be read, the machine might be faulty
                if chip_details is None:
                    logger.warn(
                        "Could not get version from chip {}, {}: {}".format(
                            x, y, result))
                    progress_bar.update()
        progress_bar.end()

        return machine, seen_chips
